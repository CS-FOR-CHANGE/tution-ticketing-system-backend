# your_app/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging

logger = logging.getLogger(__name__)


class TicketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'tickets'
        self.room_group_name = 'ticket_updates'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        logger.info(f"WebSocket disconnected with close code {close_code}")
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_message',
                    'message': message
                }
            )
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")

    # Receive message from room group
    async def broadcast_message(self, event):
        action = event['message']['action']
        ticket_data = event['message']['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'action': action,
            'message': ticket_data
        }))
