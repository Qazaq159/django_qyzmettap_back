from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreateIntent, PaymentHistory, StripeWebhook

router = DefaultRouter()
router.register(r'payments', PaymentHistory, basename='payments')

urlpatterns = [
    path('payments/create-intent/', CreateIntent.as_view()),
    path('payments/webhook/',       StripeWebhook.as_view()),
    path('', include(router.urls)),
]
