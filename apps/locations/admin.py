from django.contrib import admin

from .models import City, District


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'created_at')
    list_filter = ('city',)
    search_fields = ('name', 'city__name')
