from django.shortcuts import render

from accounts.decorators import admin_required
from orders.models import Order


@admin_required
def delivery_dashboard(request):

    orders = Order.objects.filter(
        status='Out for Delivery'
    )

    return render(request,
                  'delivery/dashboard.html',
                  {'orders': orders})