from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import UserProfile, UserEmbeddings
from django.utils import timezone

class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=False)
    is_active = serializers.BooleanField(read_only=True)
    is_admin = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'age', 'preferences', 'image', 'password', 'is_active', 'is_admin', 'created_at', 'updated_at')
        extra_kwargs = {
            'first_name': {'min_length': 1, 'max_length': 50},
            'last_name': {'min_length': 1, 'max_length': 50},
            'age': {'min_value': 0, 'max_value': 120},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)
        return super().update(instance, validated_data)

class UserCreateSerializer(UserProfileSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=True)

class UserUpdateSerializer(UserProfileSerializer):
    first_name = serializers.CharField(min_length=1, max_length=50, required=False)
    last_name = serializers.CharField(min_length=1, max_length=50, required=False)
    email = serializers.EmailField(required=False)
    age = serializers.IntegerField(min_value=0, max_value=120, required=False)
    preferences = serializers.ListField(child=serializers.CharField(), required=False)
    password = serializers.CharField(write_only=True, min_length=8, required=False)

class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid login credentials.")
        return data

class FacialRecognitionLoginSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)

    def validate_image(self, value):
        # Optionally add extra validation for image properties if necessary
        return value

class UserEmbeddingsSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = UserEmbeddings
        fields = ('id', 'user', 'embeddings')

class UserEmbeddingsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEmbeddings
        fields = ('embeddings',)