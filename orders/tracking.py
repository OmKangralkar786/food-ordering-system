import threading
import time

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def _group_name(user_id):
    return f'user_{user_id}_tracking'


def send_tracking_update(user_id, message, status='', order_id=None):
    """Push a tracking message to the user's WebSocket group."""
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        _group_name(user_id),
        {
            'type': 'order_update',
            'message': message,
            'status': status,
            'order_id': order_id,
        },
    )


def simulate_order_progress(user_id, order_id):
    """Send demo tracking steps after checkout (runs in background thread)."""
    from orders.models import Order

    # COD timing: out for delivery after 4 minutes, delivered after 6 minutes.
    steps = [
        (240, 'Rider assigned — order picked up.', 'Out for Delivery'),
        (120, 'Order delivered. Enjoy your meal!', 'Delivered'),
    ]
    for delay, message, status in steps:
        time.sleep(delay)
        Order.objects.filter(id=order_id).update(status=status)
        send_tracking_update(user_id, message, status, order_id)
