from django.utils.text import slugify
from rest_framework import serializers

from apps.locations.models import City, District
from .models import News, NewsCategory, NewsImage


class NewsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = ('id', 'name', 'created_at')
        read_only_fields = ('id', 'created_at')


class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ('id', 'news', 'image', 'is_main', 'created_at')
        read_only_fields = ('id', 'news', 'created_at')

    def validate(self, attrs):
        view = self.context.get('view')
        news_id = view.kwargs.get('pk') if view else None
        if not news_id:
            raise serializers.ValidationError('News is required.')

        news = News.objects.filter(pk=news_id).first()
        if news is None:
            raise serializers.ValidationError('News not found.')

        existing_images = news.images.count()
        if existing_images >= 5 and 'image' in attrs:
            raise serializers.ValidationError({'detail': 'Maximum 5 images per news item is allowed.'})

        if attrs.get('is_main') and news.images.filter(is_main=True).exists():
            raise serializers.ValidationError({'is_main': 'This news already has a main image.'})

        if not attrs.get('is_main') and not news.images.filter(is_main=True).exists():
            attrs['is_main'] = True

        return attrs


class NewsSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all())
    images = NewsImageSerializer(many=True, read_only=True)

    class Meta:
        model = News
        fields = (
            'id',
            'author',
            'title',
            'slug',
            'content',
            'category',
            'city',
            'district',
            'status',
            'published_at',
            'images',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'author', 'status', 'published_at', 'created_at', 'updated_at')

    def validate(self, attrs):
        city = attrs.get('city')
        district = attrs.get('district')
        if city and district and district.city_id != city.id:
            raise serializers.ValidationError({'district': 'Selected district does not belong to the selected city.'})
        return attrs

    def validate_slug(self, value):
        if not value:
            value = slugify(self.initial_data.get('title', ''))
        if not value:
            raise serializers.ValidationError('Slug cannot be empty.')
        return value

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        validated_data['status'] = News.STATUS_PENDING
        slug = validated_data.get('slug') or slugify(validated_data.get('title', ''))
        if not slug:
            raise serializers.ValidationError({'title': 'Title is required to generate the slug.'})
        validated_data['slug'] = slug
        return super().create(validated_data)


class NewsModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ('id', 'status', 'title', 'content', 'category', 'city', 'district')
        read_only_fields = ('id', 'title', 'content', 'category', 'city', 'district')

    def validate_status(self, value):
        if value not in dict(News.STATUS_CHOICES):
            raise serializers.ValidationError('Invalid status value.')
        return value

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
