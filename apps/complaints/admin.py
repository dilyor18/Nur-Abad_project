from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'target_type', 'status', 'ad', 'news', 'user', 'created_at')
    list_filter = ('target_type', 'status')
    search_fields = ('reason', 'admin_note', 'reporter__email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
