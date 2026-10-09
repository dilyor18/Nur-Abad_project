from django.conf import settings
from django.db import models

from apps.ads.models import Ad


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'ad'], name='unique_user_favorite_ad')
        ]

    def __str__(self):
        return f'{self.user.username} -> {self.ad.title}'
