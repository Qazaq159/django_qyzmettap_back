from django.urls import path
from .views import ChatListView, ChatDetailView, SendMessageView, MarkAsReadView, CreateChatView

urlpatterns = [
    path('chats/', ChatListView.as_view(), name='chat-list'),
    path('chats/<int:chat_id>/', ChatDetailView.as_view(), name='chat-detail'),
    path('chats/<int:chat_id>/send-message/', SendMessageView.as_view(), name='send-message'),
    path('chats/<int:chat_id>/read/', MarkAsReadView.as_view(), name='mark-as-read'),
    path('chats/<int:order_id>/messages', CreateChatView.as_view(), name='create-chat'),
]