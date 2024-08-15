from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import UserProfile, UserEmbeddings

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'age', 'preferences', 'image')
        extra_kwargs = {'password': {'write_only': True}}

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'age', 'preferences', 'image')

    def create(self, validated_data):
        user = UserProfile.objects.create_user(**validated_data)
        return user

class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class FaceLoginSerializer(serializers.Serializer):
    image = serializers.ImageField()

class UserEmbeddingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEmbeddings
        fields = ('id', 'user', 'embeddings')