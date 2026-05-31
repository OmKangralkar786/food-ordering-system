from django.shortcuts import render
from django.db.models import Sum, Count, Avg

from accounts.decorators import admin_required
from accounts.models import User
from orders.models import Order
from restaurants.models import Restaurant


@admin_required
def dashboard(request):
    orders = Order.objects.all()
    total_orders = orders.count()
    total_restaurants = Restaurant.objects.count()
    total_users = User.objects.count()

    revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    avg_order_value = orders.aggregate(avg=Avg('total_amount'))['avg'] or 0

    pending_orders = orders.filter(status='Pending').count()
    preparing_orders = orders.filter(status='Preparing').count()
    delivery_orders = orders.filter(status='Out for Delivery').count()
    delivered_orders = orders.filter(status='Delivered').count()

    status_breakdown = list(
        orders.values('status').annotate(count=Count('id')).order_by('-count')
    )

    recent_orders = orders.select_related('user').order_by('-created_at')[:8]

    return render(request, 'analytics/dashboard.html', {
        'total_orders': total_orders,
        'total_restaurants': total_restaurants,
        'total_users': total_users,
        'revenue': revenue,
        'avg_order_value': avg_order_value,
        'pending_orders': pending_orders,
        'preparing_orders': preparing_orders,
        'delivery_orders': delivery_orders,
        'delivered_orders': delivered_orders,
        'status_breakdown': status_breakdown,
        'recent_orders': recent_orders,
    })
