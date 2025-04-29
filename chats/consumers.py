import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Chat, Message
from channels.db import database_sync_to_async
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f"chat_{self.chat_id}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope['user'] 
        chat = await database_sync_to_async(Chat.objects.get)(id=self.chat_id)
        message_obj = await database_sync_to_async(Message.objects.create)(
            chat=chat,
            user=user,
            message=message,
            created_at=timezone.now()
        )
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message', 
                'message': message,
                'user_id': user.id,
                'created_at': message_obj.created_at.strftime('%d %b %Y %H:%M'),  # Форматируем дату
            }
        )

    async def chat_message(self, event):
        message = event['message']
        user_id = event['user_id']
        created_at = event['created_at']
        await self.send(text_data=json.dumps({
            'message': message,
            'user_id': user_id,
            'created_at': created_at
        }))
