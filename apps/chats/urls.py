from django.urls import path

from .views import ConversationListCreateAPIView, ConversationMessagesAPIView

urlpatterns = [
    path('conversations/', ConversationListCreateAPIView.as_view(), name='conversations-list'),
    path('conversations/<int:pk>/messages/', ConversationMessagesAPIView.as_view(), name='conversation-messages'),
]
