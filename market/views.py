from rest_framework import generics, permissions, status
from rest_framework.response import Response
from market.serializers import RegisterUserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserResource
from .tasks import send_confirmation_email
import logging
logger = logging.getLogger(__name__)


class MessageMixin:
    messages = {
        201: {
            "message": "CREATED"
        }
    }


class RegisterUserView(generics.CreateAPIView, MessageMixin):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs) -> Response:
        logger.warning(f"Register payload: {request.data}")
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        try:
            send_confirmation_email.apply_async(args=[user.id], ignore_result=True)
        except Exception as e:
            logger.error(f"Celery task failed: {str(e)}")
        return Response(self.messages[201], status=status.HTTP_201_CREATED)

class ProfileView(APIView):
    def get(self, request):
        user = request.user
        serializer = UserResource(user)
        return Response(serializer.data)
