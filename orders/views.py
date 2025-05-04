from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer, OrderResource, OrderRequest, UpdateOrderStatusSerializer
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.conf import settings
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@api_view(['POST'])
def create_order(request):
    if request.method == 'POST':
        serializer = OrderRequest(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = request.user  
            prepayment = (Decimal(data['budget']) * Decimal(0.1)).quantize(Decimal('0.01'))
            if user.balance < prepayment:
                return Response({'message': 'INSUFFICIENT_FUNDS',
                    'current_balance': user.balance}, status=status.HTTP_400_BAD_REQUEST)
            try:
                order = Order.objects.create(
                    title=data['title'],
                    description=data['description'],
                    budget=data['budget'],
                    deadline=data['deadline'],
                    customer=user
                )
                logger.info("Order created successfully", extra={"order_id": order.id, "user_id": user.id})
            except Exception as e:
                logger.error("Failed to create order", extra={"user_id": user.id, "error": str(e)})
                return Response({'message': 'Failed to create order'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            attached_files = []
            if 'attached_files[]' in request.data:
                try:
                    for file in request.data.getlist('attached_files[]'):
                        file_path = default_storage.save(f'uploads/{file.name}', file)
                        attached_files.append(file_path)
                    attached_files = [settings.MEDIA_URL + file for file in attached_files]
                    order.attached_files = attached_files
                    order.save()
                    logger.info("Files attached to order", extra={"order_id": order.id, "attached_files": attached_files})
                except Exception as e:
                    logger.error("Failed to attach files to order", extra={"order_id": order.id, "error": str(e)})
                    order.delete()
                    return Response({'message': 'Failed to attach files'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            user.balance -= prepayment
            user.save()
            cache_key = f"user_orders_{request.user.id}"
            cache.delete(cache_key)  
            return Response({"data": OrderResource(order).data}, status=status.HTTP_201_CREATED)
        else:
            logger.error("Order creation failed. Validation errors", extra={"errors": serializer.errors})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def my_orders(request):
    if request.user.is_authenticated:
        cache_key = f"user_orders_{request.user.id}"
        cached_orders = cache.get(cache_key)
        if cached_orders:
            return Response(cached_orders, status=status.HTTP_200_OK)
        orders = Order.objects.filter(customer=request.user)
        serializer = OrderSerializer(orders, many=True, context={'request': request})
        cache.set(cache_key, serializer.data, timeout=3600)
        return Response(serializer.data)
    return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def show_order(request, pk):
    try:
        order = Order.objects.get(id=pk)
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def destroy_order(request, pk):
    try:
        order = Order.objects.get(id=pk)
        if order.customer_id != request.user.id:
            return Response({'message': 'NOT_ALLOWED'}, status=status.HTTP_403_FORBIDDEN)
        if order.attached_files:
            files = order.attached_files
            for file_path in files:
                file_path = file_path.replace(settings.MEDIA_URL, settings.MEDIA_ROOT + "/")
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)
                    logger.info("Deleted file from order", extra={"order_id": pk, "file_path": file_path})
                else:
                    logger.warning("File not found for deletion", extra={"order_id": pk, "file_path": file_path})
        order.delete()
        logger.info("Order deleted successfully", extra={"order_id": pk, "user_id": request.user.id})
        cache_key = f"user_orders_{request.user.id}"
        cache.delete(cache_key)
        return Response({'message': 'DELETED'}, status=status.HTTP_200_OK)    
    except Order.DoesNotExist:
        logger.error("Order not found", extra={"order_id": pk})
        return Response({'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

class UpdateOrderStatusView(APIView):
    def patch(self, request, pk, *args, **kwargs):
        try:
            order = Order.objects.get(id=pk)
            if order.customer != request.user:
                return Response({"detail": "You are not authorized to update this order."}, status=status.HTTP_403_FORBIDDEN)            
            serializer = UpdateOrderStatusSerializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                order = serializer.save()
                logger.info("Order status updated successfully", extra={"order_id": pk, "user_id": request.user.id})
                cache_key = f"user_orders_{request.user.id}"
                cache.delete(cache_key)
                return Response(OrderSerializer(order, context={'request': request}).data)
            else:
                logger.error("Validation failed for updating order", extra={"order_id": pk, "errors": serializer.errors})
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        
        except Order.DoesNotExist:
            logger.error("Order not found", extra={"order_id": pk})
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        
class CurrentOrderView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.has_active_subscription():
            logger.warning("User attempted to create an order without active subscription", extra={"user_id": user.id})
            return Response({
                "message": "subscription_required",
            }, status=status.HTTP_403_FORBIDDEN)
        if not user.can_receive_new_order():
            logger.warning("User attempted to create an order, but they are in cooldown", extra={"user_id": user.id, "next_available_at": user.next_available_at()})
            return Response({
                "message": "cooldown_active",
                "next_available_at": user.next_available_at(),
            }, status=status.HTTP_403_FORBIDDEN)
        return self.create_order(user, request)
    def create_order(self, user, request):
        order = Order.objects.filter(status='open').first()
        if not order:
            logger.info("No orders available for user", extra={"user_id": user.id})
            return Response({"message": "No orders available"}, status=status.HTTP_404_NOT_FOUND)
        try:
            order.executor = user
            order.status = 'reviewing'
            order.expires_at = timezone.now() + timedelta(hours=2)
            order.save()
            user.last_received_at = timezone.now()
            user.save()
            logger.info("Order assigned to user successfully", extra={"user_id": user.id, "order_id": order.id})
            return Response(OrderSerializer(order, context={'request': request}).data)        
        except Exception as e:
            logger.error("Error while assigning order to user", extra={"user_id": user.id, "error": str(e)})
            return Response({"message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def reject_order(request, pk):
    user = request.user
    try:
        order = Order.objects.get(id=pk)
    except Order.DoesNotExist:
        logger.error("Order not found when user tried to reject", extra={"user_id": user.id, "order_id": pk})
        return Response({'message': 'Order not found'}, status=404)
    if order.executor_id != user.id:
        return Response({'message': 'You are not assigned to this order'}, status=403)
    if order.status != 'reviewing':
        logger.warning("User attempted to reject order in wrong status", extra={"user_id": user.id, "order_id": pk, "order_status": order.status})
        return Response({'message': 'Order cannot be rejected'}, status=400)
    try:
        order.executor_id = None
        order.status = 'open'
        order.expires_at = None
        order.save()
        next_available_at = user.next_available_at()
        cache_key = f"user_orders_{order.customer_id}"
        cache.delete(cache_key)
        logger.info("Order rejected successfully", extra={"user_id": user.id, "order_id": pk})
        return Response({
            'message': 'Order rejected successfully',
            'next_available_at': next_available_at,
        })
    except Exception as e:
        logger.error("Error while rejecting order", extra={"user_id": user.id, "order_id": pk, "error": str(e)})
        return Response({'message': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)