from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.locations.models import City, District


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Ad(models.Model):
    CONDITION_NEW = 'NEW'
    CONDITION_USED = 'USED'
    CONDITION_NEEDS_REPAIR = 'NEEDS_REPAIR'

    CONDITION_CHOICES = [
        (CONDITION_NEW, 'New'),
        (CONDITION_USED, 'Used'),
        (CONDITION_NEEDS_REPAIR, 'Needs Repair'),
    ]

    STATUS_ACTIVE = 'ACTIVE'
    STATUS_SOLD = 'SOLD'
    STATUS_HIDDEN = 'HIDDEN'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_SOLD, 'Sold'),
        (STATUS_HIDDEN, 'Hidden'),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ads')
    category = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='ads')
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='ads')
    district = models.ForeignKey(District, on_delete=models.PROTECT, related_name='ads')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class AdImage(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='ads/images/')
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(fields=['ad'], condition=Q(is_main=True), name='unique_main_image_per_ad')
        ]

    def __str__(self):
        return f'{self.ad.title} image'
