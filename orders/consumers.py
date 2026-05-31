import json

from channels.generic.websocket import AsyncWebsocketConsumer


class OrderConsumer(AsyncWebsocketConsumer):
    """Live order tracking WebSocket for authenticated users."""

    async def connect(self):
        user = self.scope.get('user')
        if user is None or user.is_anonymous:
            await self.close(code=4001)
            return

        self.room_group_name = f'user_{user.id}_tracking'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

        await self.send(text_data=json.dumps({
            'message': 'Connected to live order tracking.',
            'status': 'connected',
            'order_id': None,
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', '')
        except json.JSONDecodeError:
            message = text_data

        if message:
            await self.send(text_data=json.dumps({
                'message': f'Received: {message}',
                'status': 'echo',
            }))

    async def order_update(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'status': event.get('status', ''),
            'order_id': event.get('order_id'),
        }))
