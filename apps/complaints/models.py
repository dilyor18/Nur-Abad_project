from django.conf import settings
from django.db import models


class Report(models.Model):
    TARGET_AD = 'AD'
    TARGET_NEWS = 'NEWS'
    TARGET_USER = 'USER'

    TARGET_CHOICES = [
        (TARGET_AD, 'Advertisement'),
        (TARGET_NEWS, 'News'),
        (TARGET_USER, 'User'),
    ]

    STATUS_PENDING = 'PENDING'
    STATUS_IN_REVIEW = 'IN_REVIEW'
    STATUS_RESOLVED = 'RESOLVED'
    STATUS_REJECTED = 'REJECTED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_REVIEW, 'In review'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_created')
    target_type = models.CharField(max_length=20, choices=TARGET_CHOICES)
    ad = models.ForeignKey('ads.Ad', on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    news = models.ForeignKey('news.News', on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='reports_received')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    admin_note = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.target_type} report by {self.reporter.email}'
