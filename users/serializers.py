from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import UserProfile, UserEmbeddings


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'age', 'preferences', 'image')
    

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
