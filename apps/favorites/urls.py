from django.urls import path

from .views import FavoriteDeleteAPIView, FavoriteListCreateAPIView

urlpatterns = [
    path('favorites/', FavoriteListCreateAPIView.as_view(), name='favorites-list'),
    path('favorites/<int:pk>/', FavoriteDeleteAPIView.as_view(), name='favorite-detail'),
]
