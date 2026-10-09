from django.urls import path

from .views import NewsCategoryListAPIView, NewsDetailAPIView, NewsImageDeleteAPIView, NewsImageListCreateAPIView, NewsListCreateAPIView, NewsModerationAPIView

urlpatterns = [
    path('news-categories/', NewsCategoryListAPIView.as_view(), name='news-categories-list'),
    path('news/', NewsListCreateAPIView.as_view(), name='news-list'),
    path('news/<int:pk>/', NewsDetailAPIView.as_view(), name='news-detail'),
    path('news/<int:pk>/moderate/', NewsModerationAPIView.as_view(), name='news-moderate'),
    path('news/<int:pk>/images/', NewsImageListCreateAPIView.as_view(), name='news-images'),
    path('news/images/<int:pk>/', NewsImageDeleteAPIView.as_view(), name='news-image-detail'),
]
