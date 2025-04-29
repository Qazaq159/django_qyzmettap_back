import stripe, decimal
from rest_framework.views      import APIView
from rest_framework.response   import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework            import viewsets, status
from django.conf               import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators   import method_decorator
from .models                   import Payment
from .serializers              import PaymentSerializer
from market.models             import UserInstance 

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateIntent(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = decimal.Decimal(request.data.get('amount', '0'))
        if amount <= 0:
            return Response({'detail':'Invalid amount'},
                            status=status.HTTP_400_BAD_REQUEST)

        intent = stripe.PaymentIntent.create(
            amount   = int(amount * 100),
            currency = 'kzt',
            metadata = {'user_id': request.user.id},
        )
        pay = Payment.objects.create(
            user=request.user,
            amount=amount,
            stripe_intent_id=intent.id,
        )
        return Response({'client_secret': intent.client_secret,
                         'payment_id': pay.id})

class PaymentHistory(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhook(APIView):
    authentication_classes = []
    permission_classes     = []

    def post(self, request):
        payload = request.body
        sig     = request.META.get('HTTP_STRIPE_SIGNATURE')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig, settings.STRIPE_WEBHOOK_SECRET)
        except stripe.error.SignatureVerificationError:
            return Response(status=400)

        if event['type'] == 'payment_intent.succeeded':
            intent = event['data']['object']
            try:
                pay = Payment.objects.get(stripe_intent_id=intent['id'])
            except Payment.DoesNotExist:
                return Response(status=404)
            if pay.status != 'succeeded':
                pay.status = 'succeeded'
                pay.save(update_fields=['status'])
                user = pay.user
                user.balance += pay.amount
                user.save(update_fields=['balance'])
        elif event['type'] == 'payment_intent.payment_failed':
            intent = event['data']['object']
            Payment.objects.filter(stripe_intent_id=intent['id'])\
                 .update(status='failed')
        return Response(status=200)
