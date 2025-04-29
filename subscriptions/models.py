from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from market.models import UserInstance

class SubscriptionType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.PositiveIntegerField()
    duration = models.PositiveIntegerField()  
    description = models.TextField()
    features = models.JSONField()
    
    class Meta:
        indexes = [
            models.Index(fields=['name']), 
        ]

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(UserInstance, on_delete=models.CASCADE)
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['user']), 
            models.Index(fields=['subscription_type']), 
            models.Index(fields=['expires_at']), 
        ]

    def is_active(self):
        return self.expires_at > timezone.now()

    def __str__(self):
        return f"{self.user.email} - {self.subscription_type.name}"