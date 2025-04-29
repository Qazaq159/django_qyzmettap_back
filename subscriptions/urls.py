from django.urls import path
from .views import SubscriptionView, SubscriptionTypesView

urlpatterns = [
    path('subscriptions/<int:subscriptionType>/subscribe/', SubscriptionView.as_view(), name='subscribe'),
    path('subscriptions/types/', SubscriptionTypesView.as_view(), name='subscription_types'), 
]