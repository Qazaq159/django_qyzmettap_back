from django.db import models
from django.conf import settings

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending',  'Создан'),
        ('succeeded','Оплачен'),
        ('failed',   'Ошибка'),
    )
    user   = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KZT')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              default='pending')
    stripe_intent_id = models.CharField(max_length=255, unique=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.pk} | {self.user.email} | {self.amount}{self.currency}'
