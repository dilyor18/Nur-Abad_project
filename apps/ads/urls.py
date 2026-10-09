from django.urls import path

from .views import AdDetailAPIView, AdImageDeleteAPIView, AdImageListCreateAPIView, AdListCreateAPIView, CategoryListAPIView

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='categories'),
    path('ads/', AdListCreateAPIView.as_view(), name='ads-list'),
    path('ads/<int:pk>/', AdDetailAPIView.as_view(), name='ad-detail'),
    path('ads/<int:pk>/images/', AdImageListCreateAPIView.as_view(), name='ad-images'),
    path('ads/images/<int:pk>/', AdImageDeleteAPIView.as_view(), name='ad-image-detail'),
]
