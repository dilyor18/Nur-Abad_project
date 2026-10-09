from rest_framework import serializers

from apps.ads.models import Ad
from apps.news.models import News
from apps.users.models import User
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.CharField(source='reporter.username', read_only=True)

    class Meta:
        model = Report
        fields = (
            'id',
            'reporter',
            'target_type',
            'ad',
            'news',
            'user',
            'reason',
            'status',
            'admin_note',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'reporter', 'created_at', 'updated_at')

    def validate(self, attrs):
        target_type = attrs.get('target_type', getattr(self.instance, 'target_type', None))
        ad = attrs.get('ad', getattr(self.instance, 'ad', None))
        news = attrs.get('news', getattr(self.instance, 'news', None))
        target_user = attrs.get('user', getattr(self.instance, 'user', None))

        selected_targets = [value for value in (ad, news, target_user) if value is not None]
        if len(selected_targets) != 1:
            raise serializers.ValidationError('Exactly one target must be selected for a report.')

        if target_type == Report.TARGET_AD and ad is None:
            raise serializers.ValidationError({'ad': 'An ad target is required for AD reports.'})
        if target_type == Report.TARGET_NEWS and news is None:
            raise serializers.ValidationError({'news': 'A news target is required for NEWS reports.'})
        if target_type == Report.TARGET_USER and target_user is None:
            raise serializers.ValidationError({'user': 'A user target is required for USER reports.'})

        if target_type == Report.TARGET_AD and ad is not None and not Ad.objects.filter(pk=ad.pk).exists():
            raise serializers.ValidationError({'ad': 'Ad does not exist.'})
        if target_type == Report.TARGET_NEWS and news is not None and not News.objects.filter(pk=news.pk).exists():
            raise serializers.ValidationError({'news': 'News does not exist.'})
        if target_type == Report.TARGET_USER and target_user is not None and not User.objects.filter(pk=target_user.pk).exists():
            raise serializers.ValidationError({'user': 'User does not exist.'})

        return attrs

    def create(self, validated_data):
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)
