from django.shortcuts import get_object_or_404
from rest_framework import serializers

from apps.locations.models import City, District
from apps.users.models import User
from .models import Ad, AdImage, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'created_at')
        read_only_fields = ('id', 'created_at')


class AdImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdImage
        fields = ('id', 'ad', 'image', 'is_main', 'created_at')
        read_only_fields = ('id', 'ad', 'created_at')

    def validate(self, attrs):
        view = self.context.get('view')
        ad_id = view.kwargs.get('pk') if view else None
        if not ad_id:
            raise serializers.ValidationError('Ad is required.')

        ad = get_object_or_404(Ad.objects.all(), pk=ad_id)
        existing_images = ad.images.count()
        if existing_images >= 5 and 'image' in attrs:
            raise serializers.ValidationError({'detail': 'Maximum 5 images per ad is allowed.'})

        if attrs.get('is_main') and ad.images.filter(is_main=True).exists():
            raise serializers.ValidationError({'is_main': 'This ad already has a main image.'})

        if not attrs.get('is_main') and not ad.images.filter(is_main=True).exists():
            attrs['is_main'] = True

        return attrs


class AdSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all())
    images = AdImageSerializer(many=True, read_only=True)

    class Meta:
        model = Ad
        fields = (
            'id',
            'author',
            'title',
            'description',
            'price',
            'category',
            'city',
            'district',
            'condition',
            'status',
            'images',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError('Price cannot be negative.')
        return value

    def validate(self, attrs):
        city = attrs.get('city')
        district = attrs.get('district')

        if city and district and district.city_id != city.id:
            raise serializers.ValidationError({'district': 'Selected district does not belong to the selected city.'})

        if 'status' in attrs and attrs['status'] not in dict(Ad.STATUS_CHOICES):
            raise serializers.ValidationError({'status': 'Invalid status value.'})

        if 'condition' in attrs and attrs['condition'] not in dict(Ad.CONDITION_CHOICES):
            raise serializers.ValidationError({'condition': 'Invalid condition value.'})

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if request and getattr(request.user, 'is_authenticated', False):
            validated_data['author'] = request.user
        else:
            guest_user, _ = User.objects.get_or_create(
                username='guest',
                defaults={'email': 'guest@local.invalid', 'is_active': True},
            )
            validated_data['author'] = guest_user
        return super().create(validated_data)
