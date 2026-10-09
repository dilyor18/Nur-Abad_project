from django.contrib import admin

from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'ad', 'buyer', 'seller', 'created_at')
    search_fields = ('ad__title', 'buyer__username', 'seller__username')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'author', 'created_at')
    search_fields = ('author__username', 'text')
