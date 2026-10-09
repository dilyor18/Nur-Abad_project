from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Ad, AdImage, Category
from .serializers import AdImageSerializer, AdSerializer, CategorySerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class AdListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AdSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Ad.objects.select_related('author', 'category', 'city', 'district').prefetch_related('images')

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city_id=city)

        district = self.request.query_params.get('district')
        if district:
            queryset = queryset.filter(district_id=district)

        condition = self.request.query_params.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)

        if self.request.user.is_authenticated:
            queryset = queryset.filter(Q(status=Ad.STATUS_ACTIVE) | Q(author=self.request.user))
        else:
            queryset = queryset.filter(status=Ad.STATUS_ACTIVE)

        ordering = self.request.query_params.get('ordering', 'newest')
        ordering_map = {
            'newest': '-created_at',
            'oldest': 'created_at',
            'cheapest': 'price',
            'expensive': '-price',
        }
        queryset = queryset.order_by(ordering_map.get(ordering, '-created_at'))
        return queryset

    def get_permissions(self):
        if self.request.method in ('GET', 'POST'):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class AdDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Ad.objects.select_related('author', 'category', 'city', 'district').prefetch_related('images')
        if self.request.user.is_authenticated:
            return queryset.filter(Q(status=Ad.STATUS_ACTIVE) | Q(author=self.request.user))
        return queryset.filter(status=Ad.STATUS_ACTIVE)


class AdImageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AdImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        ad = get_object_or_404(Ad.objects.all(), pk=self.kwargs['pk'])
        if not self.request.user.is_authenticated and ad.status != Ad.STATUS_ACTIVE:
            raise PermissionDenied('This ad is not available.')
        if self.request.user.is_authenticated and ad.author != self.request.user and ad.status != Ad.STATUS_ACTIVE:
            raise PermissionDenied('This ad is not available.')
        return ad.images.all()

    def perform_create(self, serializer):
        ad = get_object_or_404(Ad.objects.all(), pk=self.kwargs['pk'])
        is_guest_ad = ad.author.username == 'guest'
        is_owner = self.request.user.is_authenticated and ad.author == self.request.user

        if not is_guest_ad and not is_owner:
            self.permission_denied(self.request, message='You can only upload images to your own ad.')
        if ad.images.count() >= 5:
            raise PermissionDenied('Maximum 5 images per ad is allowed.')
        if serializer.validated_data.get('is_main') is True and ad.images.filter(is_main=True).exists():
            raise PermissionDenied('This ad already has a main image.')
        if not serializer.validated_data.get('is_main') and not ad.images.filter(is_main=True).exists():
            serializer.validated_data['is_main'] = True
        serializer.save(ad=ad)


class AdImageDeleteAPIView(generics.DestroyAPIView):
    queryset = AdImage.objects.select_related('ad').all()
    serializer_class = AdImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AdImage.objects.select_related('ad').filter(ad__author=self.request.user)

    def perform_destroy(self, instance):
        if instance.ad.author != self.request.user:
            raise PermissionDenied('You can only delete your own ad images.')
        instance.delete()
