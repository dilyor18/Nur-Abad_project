from rest_framework import serializers

from apps.ads.models import Ad
from .models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    ad = serializers.PrimaryKeyRelatedField(queryset=Ad.objects.all())
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'ad', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')

    def validate_ad(self, value):
        request = self.context.get('request')
        if request and value.author == request.user:
            raise serializers.ValidationError('You cannot add your own ad to favorites.')
        if value.status != Ad.STATUS_ACTIVE:
            raise serializers.ValidationError('Only active ads can be added to favorites.')
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        if request:
            if Favorite.objects.filter(user=request.user, ad=attrs['ad']).exists():
                raise serializers.ValidationError('This ad is already in your favorites.')
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
