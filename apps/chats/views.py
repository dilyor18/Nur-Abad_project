from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class IsConversationParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in (obj.buyer, obj.seller)


class ConversationListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.select_related('ad', 'buyer', 'seller').filter(
            buyer=self.request.user
        ) | Conversation.objects.select_related('ad', 'buyer', 'seller').filter(
            seller=self.request.user
        )

    def perform_create(self, serializer):
        ad = serializer.validated_data['ad']
        if ad.author == self.request.user:
            raise PermissionDenied('You cannot start a conversation with your own ad.')

        existing = Conversation.objects.filter(ad=ad, buyer=self.request.user, seller=ad.author).first()
        if existing:
            raise ValidationError('Conversation already exists for this ad and user pair.')

        serializer.save(buyer=self.request.user, seller=ad.author)


class ConversationMessagesAPIView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['conversation'] = get_object_or_404(Conversation.objects.select_related('ad', 'buyer', 'seller'), pk=self.kwargs['pk'])
        return context

    def get_queryset(self):
        conversation = get_object_or_404(Conversation.objects.select_related('ad', 'buyer', 'seller'), pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, conversation)
        return conversation.messages.select_related('author').all()

    def perform_create(self, serializer):
        conversation = get_object_or_404(Conversation.objects.select_related('ad', 'buyer', 'seller'), pk=self.kwargs['pk'])
        if self.request.user not in (conversation.buyer, conversation.seller):
            raise PermissionDenied('You do not have access to this conversation.')
        serializer.save(author=self.request.user, conversation=conversation)
