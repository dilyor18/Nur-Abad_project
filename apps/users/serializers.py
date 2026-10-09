from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.locations.models import City, District
from .models import Profile, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_joined', 'is_staff')
        read_only_fields = ('id', 'date_joined', 'is_staff')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirmation = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirmation')

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('User with this email already exists.')
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirmation = attrs.get('password_confirmation')

        if password != password_confirmation:
            raise serializers.ValidationError({'password_confirmation': 'Passwords do not match.'})

        validate_password(password)
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        password = validated_data.pop('password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
        )
        Profile.objects.get_or_create(user=user)
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)
        self.fields['username'] = serializers.CharField(required=False, allow_blank=True)
        self.fields['email'] = serializers.EmailField(required=False, allow_blank=True)

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        if not password:
            raise serializers.ValidationError({
                'detail': 'Password is required.'
            })

        if not username and not email:
            raise serializers.ValidationError({
                'detail': 'Username or email is required.'
            })

        user = None
        if username:
            user = User.objects.filter(username__iexact=username).first()
        if user is None and email:
            user = User.objects.filter(email__iexact=email).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError({
                'detail': 'No active account found with the given credentials.'
            })

        refresh = self.get_token(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=False)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), allow_null=True, required=False)
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Profile
        fields = ('id', 'username', 'avatar', 'city', 'district', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        city = attrs.get('city', getattr(self.instance, 'city', None))
        district = attrs.get('district', getattr(self.instance, 'district', None))

        if city and district and district.city_id != city.id:
            raise serializers.ValidationError({'district': 'Selected district does not belong to the selected city.'})

        return attrs

    def update(self, instance, validated_data):
        username = validated_data.pop('username', None)
        if username is not None:
            if User.objects.filter(username__iexact=username).exclude(pk=instance.user.pk).exists():
                raise serializers.ValidationError({'username': 'This username is already taken.'})
            instance.user.username = username
            instance.user.save(update_fields=['username'])

        for field in ('avatar', 'city', 'district'):
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        instance.save()
        return instance


class PublicProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Profile
        fields = ('username', 'avatar', 'city', 'district', 'updated_at')


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name')


class DistrictSerializer(serializers.ModelSerializer):
    city = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = District
        fields = ('id', 'name', 'city')
