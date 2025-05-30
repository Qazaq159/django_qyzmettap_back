import logging
import stripe, decimal 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Payment
from .serializers import PaymentSerializer
from market.models import UserInstance 

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateIntent(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = decimal.Decimal(request.data.get('amount', '0'))
        if amount <= 0:
            logger.warning("Invalid payment amount", extra={"user_id": request.user.id, "amount": str(amount)})
            return Response({'detail': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency='kzt',
                metadata={'user_id': request.user.id},
            )
            pay = Payment.objects.create(
                user=request.user,
                amount=amount,
                stripe_intent_id=intent.id,
            )
            logger.info("PaymentIntent created", extra={"user_id": request.user.id, "payment_id": pay.id, "amount": str(amount)})
            return Response({'client_secret': intent.client_secret, 'payment_id': pay.id})
        except Exception as e:
            logger.error("Failed to create PaymentIntent", extra={"user_id": request.user.id, "error": str(e)})
            return Response({'detail': 'Payment creation failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentHistory(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        logger.info("User requested payment history", extra={"user_id": self.request.user.id})
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhook(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            sig = request.META.get('HTTP_STRIPE_SIGNATURE')
            payload = request.body

            logger.warning("Received Stripe webhook", extra={
                "body": payload.decode(errors="ignore"),
                "signature": sig
            })

            # Верификация события от Stripe
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig,
                secret=settings.STRIPE_WEBHOOK_SECRET
            )

            intent = event['data']['object']
            event_type = event['type']

            if event_type == 'payment_intent.succeeded':
                try:
                    pay = Payment.objects.get(stripe_intent_id=intent['id'])
                except Payment.DoesNotExist:
                    logger.warning("PaymentIntent succeeded, but Payment not found", extra={"stripe_intent_id": intent['id']})
                    return Response(status=404)

                if pay.status != 'succeeded':
                    pay.status = 'succeeded'
                    pay.save(update_fields=['status'])

                    user = pay.user
                    user.balance += pay.amount
                    user.save(update_fields=['balance'])

                    logger.info("Payment succeeded and user balance updated", extra={
                        "user_id": user.id,
                        "payment_id": pay.id,
                        "amount": str(pay.amount)
                    })

            elif event_type == 'payment_intent.payment_failed':
                Payment.objects.filter(stripe_intent_id=intent['id']).update(status='failed')
                logger.warning("Payment failed", extra={"stripe_intent_id": intent['id']})

            return Response(status=200)

        except stripe.error.SignatureVerificationError as e:
            logger.error("Invalid Stripe signature", extra={"error": str(e)})
            return Response(status=400)

        except Exception as e:
            logger.exception("Unexpected error in Stripe webhook", extra={"error": str(e)})
            return Response(status=500)