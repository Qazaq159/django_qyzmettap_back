from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import UserInstance
import logging

@shared_task
def send_confirmation_email(user_id):
    logger = logging.getLogger(__name__)
    logger.warning(f"Sending email to user_id={user_id}")
    user = UserInstance.objects.get(id=user_id)
    
    subject = 'Welcome to Our Platform'
    message = f"Hello {user.name},\n\nThank you for registering on our platform. Your account has been successfully created.\n\nBest regards,\nTeam"
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(
        subject,
        message,
        from_email,
        [user.email], 
        fail_silently=False
    )
    
    return f"Confirmation email sent to {user.email}."
