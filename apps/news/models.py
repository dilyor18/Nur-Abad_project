from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.locations.models import City, District


class NewsCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class News(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_PUBLISHED = 'PUBLISHED'
    STATUS_REJECTED = 'REJECTED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='news')
    category = models.ForeignKey('NewsCategory', on_delete=models.PROTECT, related_name='news')
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='news')
    district = models.ForeignKey(District, on_delete=models.PROTECT, related_name='news')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        elif self.status != self.STATUS_PUBLISHED:
            self.published_at = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class NewsImage(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='news/images/')
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(fields=['news'], condition=Q(is_main=True), name='unique_main_news_image')
        ]

    def __str__(self):
        return f'{self.news.title} image'
