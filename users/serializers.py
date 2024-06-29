from rest_framework import serializers
from .models import UserProfile, UserImage, UserEmbeddings

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'first_name', 'last_name', 'email', 'age', 'preferences')

class UserImageSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = UserImage
        fields = ('id', 'user', 'image')

class UserEmbeddingsSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = UserEmbeddings
        fields = ('id', 'user', 'embeddings')
