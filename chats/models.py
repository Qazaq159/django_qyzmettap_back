from django.db import models
from orders.models import Order
from market.models import UserInstance

class Chat(models.Model):
    order = models.ForeignKey(Order, related_name='chats', on_delete=models.CASCADE)
    customer = models.ForeignKey(UserInstance, related_name='customer_chats', on_delete=models.CASCADE)
    executor = models.ForeignKey(UserInstance, related_name='executor_chats', on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['executor']),
        ]

    def get_participant(self, user_id):
        if self.customer.id != user_id:
            return self.customer
        return self.executor

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(UserInstance, related_name='messages', on_delete=models.CASCADE)
    message = models.TextField()
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['chat']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
            models.Index(fields=['read_at']),
        ]