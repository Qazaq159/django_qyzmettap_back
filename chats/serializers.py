from rest_framework import serializers
from .models import Chat, Message, Order

class MessageSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d %b %Y %H:%M')
    class Meta:
        model = Message
        fields = ['id', 'user_id', 'message', 'created_at', 'read_at']

class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True)
    class Meta:
        model = Chat
        fields = ['id', 'order', 'messages']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        current_user = self.context['request'].user.id
        participant = instance.get_participant(current_user)
        representation['participant'] = {'id': participant.id, 'name': participant.name}
        return representation

class ChatListSerializer(serializers.ModelSerializer):
    message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    title = serializers.CharField(source='order.title')
    status = serializers.CharField(source='order.status')  
    participant = serializers.SerializerMethodField() 
    class Meta:
        model = Chat
        fields = ['id', 'title', 'status','participant', 'message', 'unread_count']

    def get_message(self, obj):
        last_message = obj.messages.latest('created_at')
        return {
            'id': last_message.id,
            'user_id': last_message.user.id,
            'message': last_message.message,
            'created_at': last_message.created_at.strftime('%d %b %Y %H:%M')
        }

    def get_unread_count(self, obj):
        return obj.messages.filter(user_id=obj.customer.id).filter(read_at__isnull=True).count()
    
    def get_participant(self, obj):
        user_id = self.context['request'].user.id 
        participant = obj.get_participant(user_id)
        return {
            'id': participant.id,
            'name': participant.name,
        }

