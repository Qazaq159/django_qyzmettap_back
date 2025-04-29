from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Chat, Message, Order
from .serializers import ChatSerializer, ChatListSerializer
from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class ChatListView(APIView):
    def get(self, request):
        user = request.user
        chats = Chat.objects.filter(customer=user) | Chat.objects.filter(executor=user)
        serializer = ChatListSerializer(chats, many=True, context={'request': request})
        return Response(serializer.data)

class ChatDetailView(APIView):
    def get(self, request, chat_id):
        chat = Chat.objects.get(id=chat_id)
        serializer = ChatSerializer(chat, context={'request': request})
        return Response(serializer.data)

class SendMessageView(APIView):
    def post(self, request, chat_id):
        chat = Chat.objects.get(id=chat_id)
        user = request.user
        if user not in [chat.customer, chat.executor]:
            return Response({"message": "FORBIDDEN"}, status=status.HTTP_403_FORBIDDEN)
        message_data = request.data.get("message")
        message = Message.objects.create(
            chat=chat,
            user=user,
            message=message_data
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{chat_id}",
            {
                'type': 'chat_message',
                'message': message_data,
                'user_id': user.id,
                'created_at': message.created_at.strftime('%d %b %Y %H:%M')
            }
        )
        return Response(ChatSerializer(chat, context={'request': request}).data)

class MarkAsReadView(APIView):
    def post(self, request, chat_id):
        user = request.user
        chat = Chat.objects.get(id=chat_id)
        chat.messages.exclude(user__id=user.id).filter(read_at__isnull=True).update(read_at=datetime.now())
        return Response(status=status.HTTP_204_NO_CONTENT)

class CreateChatView(APIView):
    def post(self, request, order_id):
        user = request.user
        order = Order.objects.get(id=order_id)
        if user.id != order.executor.id:
            return Response({"error": "Only the assigned executor can start the chat."}, status=status.HTTP_403_FORBIDDEN)
        chat = Chat.objects.create(
            order=order,
            customer=order.customer,
            executor=order.executor,
        )
        message = request.data.get('message')
        Message.objects.create(
            chat=chat,
            user=user,
            message=message
        )
        return Response(ChatSerializer(chat, context={'request': request}).data)
