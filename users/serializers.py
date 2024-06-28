from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserImage, UserEmbeddings

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'age', 'preferences')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            age=validated_data.get('age'),
            preferences=validated_data.get('preferences')
        )
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.age = validated_data.get('age', instance.age)
        instance.preferences = validated_data.get('preferences', instance.preferences)
        instance.save()
        return instance


class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = ('id', 'user', 'image')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = UserProfileSerializer(instance.user).data
        return representation


class UserEmbeddingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEmbeddings
        fields = ('id', 'user', 'embeddings')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = UserProfileSerializer(instance.user).data
        return representation
