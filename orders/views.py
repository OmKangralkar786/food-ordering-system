import threading

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import Cart, CartItem, Order, OrderItem, Coupon, Notification, Payment
from menu.models import MenuItem

from firebase_admin import messaging


def send_push_notification(device_token):
    message = messaging.Message(
        notification=messaging.Notification(
            title='Order Confirmed',
            body='Your order has been placed successfully.'
        ),
        token=device_token,
    )
    response = messaging.send(message)
    return response


@login_required
def map_view(request):
    latest_order = (
        Order.objects.filter(user=request.user)
        .prefetch_related('orderitem_set__menu_item__restaurant')
        .order_by('-created_at')
        .first()
    )

    restaurant_name = 'FoodHub Restaurant'
    restaurant_address = 'MG Road, Belgaum, Karnataka, India'
    order_status = 'Out for Delivery'

    if latest_order:
        order_status = latest_order.status
        first_item = latest_order.orderitem_set.select_related(
            'menu_item__restaurant'
        ).first()
        if first_item and first_item.menu_item.restaurant:
            r = first_item.menu_item.restaurant
            restaurant_name = r.name
            restaurant_address = f'{r.address}, Belgaum, Karnataka, India'

    delivery_address = request.user.address or 'Ramdev Nagar, Belgaum, Karnataka, India'
    if 'belgaum' not in delivery_address.lower() and 'belagavi' not in delivery_address.lower():
        delivery_address = f'{delivery_address}, Belgaum, Karnataka, India'

    return render(request, 'orders/map.html', {
        'api_key': settings.GOOGLE_MAPS_API_KEY,
        'restaurant_name': restaurant_name,
        'restaurant_address': restaurant_address,
        'delivery_address': delivery_address,
        'order_status': order_status,
        'order_id': latest_order.id if latest_order else None,
    })

# ADD TO CART
@login_required
def add_to_cart(request, item_id):

    # Get menu item
    menu_item = get_object_or_404(
        MenuItem,
        id=item_id,
        available=True
    )

    # Get or create user cart
    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        menu_item=menu_item
    )

    # If item already exists increase quantity
    if not created:
        cart_item.quantity += 1

    # Save cart item
    cart_item.save()

    return redirect('view_cart')


# DECREASE CART ITEM
@login_required
def decrease_cart_item(request, item_id):

    # Get cart item
    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    # Reduce quantity
    if cart_item.quantity > 1:

        cart_item.quantity -= 1
        cart_item.save()

    else:
        # Remove item if quantity becomes 0
        cart_item.delete()

    return redirect('view_cart')


# REMOVE COMPLETE ITEM
@login_required
def remove_from_cart(request, item_id):

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    cart_item.delete()

    return redirect('view_cart')


def _cart_subtotal(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    items = CartItem.objects.filter(cart=cart)
    return sum(item.total_price() for item in items), items


@login_required
def view_cart(request):
    subtotal, items = _cart_subtotal(request.user)
    discount = request.session.get('coupon', 0)
    total = max(subtotal - discount, 0)

    today = timezone.now().date()
    available_coupons = Coupon.objects.filter(
        active=True,
        expiry_date__gte=today,
    ).order_by('-discount')

    applied_coupon_id = request.session.get('applied_coupon_id')

    return render(request, 'orders/cart.html', {
        'items': items,
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
        'available_coupons': available_coupons,
        'applied_coupon_id': applied_coupon_id,
        'applied_coupon_code': request.session.get('applied_coupon_code', ''),
    })


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('view_cart')


def _finalize_order(order, request):
    send_mail(
        'Order Confirmed',
        f'Your Order #{order.id} has been placed successfully.',
        'yourgmail@gmail.com',
        [request.user.email],
        fail_silently=False,
    )

    Notification.objects.create(
        user=request.user,
        message=f'Your order #{order.id} is confirmed.'
    )

    from .tracking import send_tracking_update, simulate_order_progress
    send_tracking_update(
        request.user.id,
        f'Order #{order.id} placed successfully.',
        'Pending',
        order.id,
    )
    threading.Thread(
        target=simulate_order_progress,
        args=(request.user.id, order.id),
        daemon=True,
    ).start()


@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items.exists():
        return redirect('view_cart')

    subtotal = sum(item.total_price() for item in cart_items)
    discount = request.session.get('coupon', 0)
    total = max(subtotal - discount, 0)
    order = Order.objects.create(
        user=request.user,
        total_amount=total
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            menu_item=item.menu_item,
            quantity=item.quantity,
            price=item.menu_item.price
        )

    cart_items.delete()
    request.session.pop('coupon', None)
    request.session.pop('applied_coupon_id', None)
    request.session.pop('applied_coupon_code', None)

    return render(request, 'orders/payment_select.html', {
        'order': order,
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
    })


@login_required
def payment_options(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/payment_select.html', {
        'order': order,
    })


@login_required
def cod_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method != 'POST':
        return redirect('payment_options', order_id=order.id)

    Payment.objects.create(
        order=order,
        payment_id='COD',
        amount=order.total_amount,
        paid=False,
    )

    _finalize_order(order, request)

    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def apply_coupon(request):
    if request.method == 'POST':
        coupon_id = request.POST.get('coupon_id')
        subtotal, _ = _cart_subtotal(request.user)
        today = timezone.now().date()

        if not coupon_id:
            messages.error(request, 'Please select a coupon to apply.')
            return redirect('view_cart')

        try:
            coupon = Coupon.objects.get(
                id=coupon_id,
                active=True,
                expiry_date__gte=today,
            )
        except Coupon.DoesNotExist:
            messages.error(request, 'This coupon is invalid or has expired.')
            return redirect('view_cart')

        if subtotal < coupon.minimum_amount:
            messages.error(
                request,
                f'Minimum order of ₹{coupon.minimum_amount} required for coupon {coupon.code}.',
            )
            return redirect('view_cart')

        request.session['coupon'] = coupon.discount
        request.session['applied_coupon_id'] = coupon.id
        request.session['applied_coupon_code'] = coupon.code
        messages.success(request, f'Coupon "{coupon.code}" applied! You saved ₹{coupon.discount}.')

    return redirect('view_cart')


@login_required
def remove_coupon(request):
    request.session.pop('coupon', None)
    request.session.pop('applied_coupon_id', None)
    request.session.pop('applied_coupon_code', None)
    messages.info(request, 'Coupon removed.')
    return redirect('view_cart')


@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'orders/notifications.html', {
        'notifications': user_notifications
    })


@login_required
def tracking_page(request):
    latest_order = Order.objects.filter(user=request.user).order_by('-created_at').first()
    return render(request, 'orders/tracking.html', {
        'latest_order': latest_order,
    })




@login_required
def order_history(request):
    """Display all orders for the logged-in user"""
    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related('orderitem_set__menu_item').order_by('-created_at')
    
    return render(request, 'orders/order_history.html', {
        'orders': orders,
    })
