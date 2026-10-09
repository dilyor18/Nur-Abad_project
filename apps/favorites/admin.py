from django.contrib import admin

from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ad', 'created_at')
    search_fields = ('user__username', 'ad__title')
