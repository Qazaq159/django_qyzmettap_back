from django.db import models
from market.models import UserInstance
from django.utils import timezone

class Order(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('reviewing', 'Reviewing'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    customer = models.ForeignKey(UserInstance, related_name='orders', on_delete=models.CASCADE)
    executor = models.ForeignKey(UserInstance, related_name='assigned_orders', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default='open')
    attached_files = models.JSONField(null=True, blank=True)
    deadline = models.IntegerField(null=True, blank=True) 
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['customer']),
            models.Index(fields=['executor']),
        ]

    def __str__(self):
        return self.title

    def time_since_created(self):
        delta = timezone.now() - self.created_at
        seconds = delta.total_seconds()
        if seconds < 60:
            return f"{int(seconds)} seconds ago"
        elif seconds < 3600:
            return f"{int(seconds // 60)} minutes ago"
        elif seconds < 86400:
            return f"{int(seconds // 3600)} hours ago"
        return f"{int(seconds // 86400)} days ago"
