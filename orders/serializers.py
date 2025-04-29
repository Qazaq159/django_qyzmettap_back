from rest_framework import serializers
from .models import Order
from market.serializers import UserResource

class OrderSerializer(serializers.ModelSerializer):  
    created_at = serializers.SerializerMethodField()
    attached_files = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id', 'title', 'description', 'budget', 'status', 'attached_files', 'deadline', 'expires_at', 'created_at']
    
    def get_created_at(self, obj):
        return obj.time_since_created()
    
    def get_attached_files(self, obj):
        if obj.attached_files:
            return [f"http://localhost:8000{file}" for file in obj.attached_files]
        return []
    
    def get_executor(self, obj):
        if obj.executor:
            return UserResource(obj.executor).data
        return None
    
    def get_customer(self, obj):
        if obj.customer:
            return UserResource(obj.customer).data
        return None
    
    def to_representation(self, instance):
        user = self.context.get('request').user  
        representation = super().to_representation(instance)
        if instance.customer.id == user.id:
            representation['executor'] = self.get_executor(instance)
        elif instance.executor and instance.executor.id == user.id:
            representation['customer'] = self.get_customer(instance)
        return representation

class OrderRequest(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    budget = serializers.DecimalField(max_digits=10, decimal_places=2)
    deadline = serializers.IntegerField(required=True)
    status = serializers.CharField(default="open")

class OrderResource(serializers.ModelSerializer):
    attached_files = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id', 'title', 'description', 'budget', 'status', 'attached_files', 'deadline', 'created_at']
    def get_attached_files(self, obj):
        if obj.attached_files:
            return [f"http://localhost:8000{file}" for file in obj.attached_files]
        return []
    
class UpdateOrderStatusSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    class Meta:
        model = Order
        fields = ['status']