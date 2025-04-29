from rest_framework import generics, permissions, status
from rest_framework.response import Response
from market.serializers import RegisterUserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserResource
from .tasks import send_confirmation_email


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
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_confirmation_email.apply_async(args=[user.id])
        return Response(self.messages[201], status=status.HTTP_201_CREATED)

class ProfileView(APIView):
    def get(self, request):
        user = request.user
        serializer = UserResource(user)
        return Response(serializer.data)
