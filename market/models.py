from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class UserInstance(AbstractUser):
    ROLE_CUSTOMER = 'CUSTOMER'
    ROLE_DEVELOPER = 'DEVELOPER'
    ROLE_CHOICES = (
        (ROLE_DEVELOPER, 'developer'),
        (ROLE_CUSTOMER, 'customer'),
    )

    name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=255, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    username = models.CharField(max_length=255, blank=True, null=True)
    last_received_at = models.DateTimeField(null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=2000.00)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    class Meta:
        verbose_name = ''
        verbose_name_plural = ''

    def __str__(self):
        return f'<User ({self.pk}) {self.email}>'

    def can_receive_new_order(self):
        if not self.last_received_at:
            return True
        return timezone.now() > self.last_received_at + timedelta(hours=2)

    def next_available_at(self):
        if not self.last_received_at:
            return "Available now"
        next_available_time = self.last_received_at + timedelta(hours=2)
        return next_available_time.strftime('%H:%M %d.%m.%Y')
    
    def has_active_subscription(self):
        active_subscription = self.subscription_set.filter(expires_at__gt=timezone.now()).first()
        if active_subscription:
            return True
        return False
