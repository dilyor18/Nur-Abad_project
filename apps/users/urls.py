from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginAPIView, MeAPIView, ProfileMeAPIView, PublicProfileAPIView, RegisterAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeAPIView.as_view(), name='me'),
    path('profile/', ProfileMeAPIView.as_view(), name='profile_me'),
    path('profile/<str:username>/', PublicProfileAPIView.as_view(), name='public_profile'),
]
