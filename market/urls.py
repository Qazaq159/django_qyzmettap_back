from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from market.views import RegisterUserView, ProfileView


urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/', TokenRefreshView.as_view(), name='token'),
    path('user/profile/', ProfileView.as_view(), name='profile'),
]

