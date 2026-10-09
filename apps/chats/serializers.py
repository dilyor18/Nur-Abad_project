from django.core.exceptions import ValidationError
from rest_framework import serializers

from apps.ads.models import Ad
from .models import Conversation, Message


class ConversationSerializer(serializers.ModelSerializer):
    ad = serializers.PrimaryKeyRelatedField(queryset=Ad.objects.all())
    buyer = serializers.StringRelatedField(read_only=True)
    seller = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Conversation
        fields = ('id', 'ad', 'buyer', 'seller', 'created_at')
        read_only_fields = ('id', 'buyer', 'seller', 'created_at')

    def validate_ad(self, value):
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        ad = validated_data['ad']
        if Conversation.objects.filter(ad=ad, buyer=request.user, seller=ad.author).exists():
            return Conversation.objects.get(ad=ad, buyer=request.user, seller=ad.author)
        return Conversation.objects.create(buyer=request.user, seller=ad.author, ad=ad)


class MessageSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    conversation = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'conversation', 'author', 'text', 'created_at')
        read_only_fields = ('id', 'conversation', 'author', 'created_at')

    def validate_text(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Message text cannot be empty.')
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        conversation = self.context.get('conversation')
        if request and conversation:
            if request.user not in (conversation.buyer, conversation.seller):
                raise ValidationError('You do not have access to this conversation.')
        validated_data['author'] = request.user
        validated_data['conversation'] = conversation
        return super().create(validated_data)
