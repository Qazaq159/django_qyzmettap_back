from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Subscription, SubscriptionType
from .serializers import SubscriptionSerializer, SubscriptionTypeSerializer
from datetime import timedelta
from django.utils import timezone
from rest_framework import status

class SubscriptionView(APIView):
    def post(self, request, subscriptionType, *args, **kwargs):
        user = request.user
        try:
            subscription_type = SubscriptionType.objects.get(id=subscriptionType)
        except SubscriptionType.DoesNotExist:
            return Response({"message": "Subscription type not found"}, status=status.HTTP_404_NOT_FOUND)
        if user.balance < subscription_type.price:
            return Response({"message": "Insufficient funds", "current_balance": user.balance}, status=status.HTTP_400_BAD_REQUEST)
        user.balance -= subscription_type.price
        user.save()
        subscription, created = Subscription.objects.update_or_create(
            user=user,
            subscription_type=subscription_type,
            defaults={"expires_at": timezone.now() + timedelta(days=subscription_type.duration)}
        )
        return Response(SubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED)


class SubscriptionTypesView(APIView):
    def get(self, request, *args, **kwargs):
        subscription_types = SubscriptionType.objects.all()
        return Response(SubscriptionTypeSerializer(subscription_types, many=True).data)
