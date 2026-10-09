from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError

from .models import Favorite
from .serializers import FavoriteSerializer


class FavoriteListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.select_related('user', 'ad').filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteDeleteAPIView(generics.DestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.select_related('user', 'ad').filter(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise ValidationError('You cannot delete someone else\'s favorite.')
        instance.delete()
