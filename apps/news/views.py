from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination

from .models import News, NewsCategory, NewsImage
from .serializers import NewsCategorySerializer, NewsImageSerializer, NewsModerationSerializer, NewsSerializer


class DefaultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NewsCategoryListAPIView(generics.ListAPIView):
    serializer_class = NewsCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = NewsCategory.objects.all()


class NewsListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = NewsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        queryset = News.objects.select_related('author', 'category', 'city', 'district').prefetch_related('images')
        if not self.request.user.is_staff:
            queryset = queryset.filter(status=News.STATUS_PUBLISHED)

        district_id = self.request.query_params.get('district')
        city_id = self.request.query_params.get('city')
        category_id = self.request.query_params.get('category')

        if district_id:
            queryset = queryset.filter(district_id=district_id)
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset.order_by('-published_at', '-created_at')


class NewsDetailAPIView(generics.RetrieveAPIView):
    serializer_class = NewsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = News.objects.select_related('author', 'category', 'city', 'district').prefetch_related('images')
        if not self.request.user.is_staff:
            queryset = queryset.filter(status=News.STATUS_PUBLISHED)
        return queryset


class NewsModerationAPIView(generics.UpdateAPIView):
    serializer_class = NewsModerationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = News.objects.all()

    def get_object(self):
        obj = get_object_or_404(News.objects.all(), pk=self.kwargs['pk'])
        if not self.request.user.is_staff:
            raise PermissionDenied('Only admins can moderate news.')
        return obj


class NewsImageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = NewsImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        news = get_object_or_404(News.objects.all(), pk=self.kwargs['pk'])
        return news.images.all()

    def perform_create(self, serializer):
        news = get_object_or_404(News.objects.all(), pk=self.kwargs['pk'])
        serializer.save(news=news)


class NewsImageDeleteAPIView(generics.DestroyAPIView):
    serializer_class = NewsImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = NewsImage.objects.all()
