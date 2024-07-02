from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import UserProfile, UserImage, UserEmbeddings

class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = ('image',)

class UserProfileSerializer(serializers.ModelSerializer):
    image = UserImageSerializer(write_only=True)  # Nest the image serializer

    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'age', 'preferences', 'image')

    def create(self, validated_data):
        image_data = validated_data.pop('image')
        user = UserProfile.objects.create(**validated_data)
        UserImage.objects.create(user=user, **image_data)
        return user
    

class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        # Optionally add extra validation to check credentials
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
