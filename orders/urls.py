from django.urls import path
from . import views
from .views import (
    add_to_cart,
    view_cart,
    remove_from_cart,
    checkout,
    payment_options,
    cod_payment,
    apply_coupon,
    remove_coupon,
    notifications,
    tracking_page,
    map_view,
    order_history,
)


urlpatterns = [

    path('add/<int:item_id>/', add_to_cart, name='add_to_cart'),

    path('cart/', view_cart, name='view_cart'),

    path('remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),

    path('checkout/', checkout, name='checkout'),

    path('payment-options/<int:order_id>/', payment_options, name='payment_options'),
    path('cod/<int:order_id>/', cod_payment, name='cod_payment'),

    path('apply-coupon/', apply_coupon, name='apply_coupon'),
    path('remove-coupon/', remove_coupon, name='remove_coupon'),

    path('notifications/',notifications,name='notifications'),

    path('tracking/',tracking_page,name='tracking_page'),

    path('map/',map_view,name='map_view'),

    path('history/', order_history, name='order_history'),

     # ADD TO CART
    path('add-to-cart/<int:item_id>/',views.add_to_cart,name='add_to_cart'),

    # VIEW CART
    path('cart/',views.view_cart,name='view_cart'),

    # DECREASE QUANTITY
    path('cart/decrease/<int:item_id>/',views.decrease_cart_item,name='decrease_cart_item'),

    # REMOVE ITEM
    path('remove-from-cart/<int:item_id>/',views.remove_from_cart,name='remove_from_cart'),

    # CHECKOUT
    path('checkout/',views.checkout,name='checkout'),

]