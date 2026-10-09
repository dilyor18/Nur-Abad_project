from django.contrib import admin

from .models import News, NewsCategory, NewsImage


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'city', 'district', 'created_at')
    list_filter = ('status', 'category', 'city', 'district')
    search_fields = ('title', 'content', 'author__email')
    readonly_fields = ('created_at', 'updated_at', 'published_at')
    ordering = ('-created_at',)


@admin.register(NewsImage)
class NewsImageAdmin(admin.ModelAdmin):
    list_display = ('news', 'image', 'is_main', 'created_at')
    list_filter = ('is_main',)
