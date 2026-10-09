from django.contrib import admin

from .models import Ad, AdImage, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'category', 'city', 'district', 'price', 'condition', 'status', 'created_at')
    list_filter = ('status', 'condition', 'category', 'city')
    search_fields = ('title', 'description', 'author__email')


@admin.register(AdImage)
class AdImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'ad', 'image', 'is_main')
    list_filter = ('is_main',)
    search_fields = ('ad__title',)
