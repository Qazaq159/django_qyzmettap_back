import re
from django.contrib.auth import get_user_model
from rest_framework import serializers
from subscriptions.models import Subscription
from datetime import datetime

class RegisterUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, max_length=255)
    phone = serializers.CharField(write_only=True, max_length=11)
    password = serializers.CharField(write_only=True, max_length=255)
    password_confirmation = serializers.CharField(write_only=True, max_length=255)

    class Meta:
        model = get_user_model()
        fields = ('password', 'phone', 'email', 'role', 'password_confirmation', 'name')

    def create(self, validated_data):
        validated_data['username'] = 'empty'
        validated_data.pop('password_confirmation')
        return get_user_model().objects.create_user(**validated_data)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError(
                {
                    'password': 'Passwords do not match.'
                }
            )

        if not re.match(r'^\+?[78]([0-9]{10})$', attrs['phone']):
            raise serializers.ValidationError(
                {
                    'phone': 'Phone number must be as "7XXXQQQAABB"'
                }
            )

        if get_user_model().objects.filter(phone=attrs['phone']).exists():
            raise serializers.ValidationError(
                {
                    'phone': 'User with this phone number already exists.'
                }
            )
        return attrs

class UserResource(serializers.ModelSerializer):
    subscription = serializers.SerializerMethodField()
    class Meta:
        model = get_user_model()
        fields = ['id', 'name', 'phone', 'email', 'role', 'balance', 'subscription']
    
    def get_subscription(self, obj):
        if obj.role == 'DEVELOPER':
            subscription = Subscription.objects.filter(user=obj).first()
            if subscription and subscription.is_active():
                expires_at = subscription.expires_at.strftime('%d %b %Y %H:%M') 
                return {
                    'isActive': True, 
                    'expiresAt': expires_at, 
                }
        return None