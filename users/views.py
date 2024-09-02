from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from drf_spectacular import openapi
from django.db import transaction
from django.contrib.auth import login, authenticate
from utils.match_face import FaceMatch
from utils.facial_processing import FacialProcessing
from .models import UserProfile, UserEmbeddings
from .forms import EmailLoginForm
from .serializers import (
    UserProfileSerializer, 
    EmailLoginSerializer, 
    FacialRecognitionLoginSerializer, 
    UserEmbeddingsSerializer, 
    UserEmbeddingsCreateSerializer
)
import tempfile
import os
from rest_framework.exceptions import ValidationError

class UserSignUpAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'first_name': {
                        'type': 'string',
                        'description': 'First name of the new user.'
                    },
                    'last_name': {
                        'type': 'string',
                        'description': 'Last name of the new user.'
                    },
                    'email': {
                        'type': 'string', 
                        'format': 'email',
                        'description': 'Email address of the new user. Must be unique.'
                    },
                    'password': {
                        'type': 'string',
                        'format': 'password',
                        'description': 'Password for the new user.'
                    },
                    'age': {
                        'type': 'integer',
                        'description': 'Age of the new user. Must be an integer.'
                    },
                    'preferences': {
                        'type': 'string',
                        'description': 'Food Preferences of User',
                    },
                }
            }
        },
        responses={201: UserProfileSerializer},
        description="Register a new user and their facial data for recognition.",
        examples=[
            OpenApiExample(
                "Example 1",
                summary="Example of a valid request",
                description="This is what a valid request might look like",
                value={
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "age": 30,
                    "preferences": "None",
                }
            )
        ]
    )        

    def post(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    user.set_password(request.data["password"])
                    user.save()

                    token, _ = Token.objects.get_or_create(user=user)  # Corrected 'object' to 'objects'
                    return Response({
                        'status': 'Success',
                        'message': 'User data registered successfully',
                        'token_key': token.key
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'status': 'Error',
                    'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserEmbeddingsSetupView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Setup facial embeddings for the authenticated user.",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {
                        'type': 'string', 
                        'format': 'binary',
                        'description':'Face Image Uploaded by User'
                    },
                }
            }
        },
        responses={
            200: {
                'description': 'Embeddings setup successful',
                'content': {
                    'application/json': {
                        'example': {
                            'status': 'Success',
                            'message': 'Embeddings setup successful'
                        }
                    }
                }
            },
            400: {
                'description': 'Invalid or missing embeddings',
                'content': {
                    'application/json': {
                        'example': {
                            'status': 'Error',
                            'message': 'Invalid or missing embeddings'
                        }
                    }
                }
            }
        },
        examples=[
            OpenApiExample(
                name="Embeddings Setup Example",
                summary="Example of setting up facial embeddings for the user.",
                description="A valid example showing how to set up facial embeddings for the user.",
                value={
                    "image": "path/to/your/image.jpg"
                },
                request_only=True
            ),
            OpenApiExample(
                name="Successful Embeddings Setup Response",
                summary="Successful embeddings setup response.",
                description="Response returned after successfully setting up facial embeddings for the user.",
                value={
                    "status": "Success",
                    "message": "Embeddings setup successful"
                },
                response_only=True
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        # Importing inside the method to avoid potential circular imports
        from rest_framework.parsers import MultiPartParser, FormParser
        request.parser_classes = [MultiPartParser, FormParser]

        image = request.FILES.get("image")
        if not image:
            return Response({
                'status': 'Error',
                'message': 'Image file is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        face_processor = FacialProcessing()

        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in image.chunks():
                    temp_file.write(chunk)
                temp_file.flush()
                image_path = temp_file.name

            embeddings = face_processor.extract_embeddings_vgg(image_path)
            if not embeddings:
                raise ValidationError("Failed to process face.")

            # Remove the temporary file after processing
            os.remove(image_path)

            # Save embeddings
            embeddings_serializer = UserEmbeddingsCreateSerializer(data={'embeddings': embeddings})
            if embeddings_serializer.is_valid():
                embeddings_instance = embeddings_serializer.save(user=request.user)
                return Response(
                    {
                        'status': 'Success',
                        'message': 'Embeddings setup successful'
                    }, status=status.HTTP_200_OK)
            return Response(
                {
                    'status': 'Error',
                    'message': 'Invalid or missing embeddings'
                }, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as ve:
            return Response({
                'status': 'Error',
                'message': str(ve)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'Error',
                'message': 'An unexpected error occurred.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailLoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        description="Authenticate a user using their email and password.",
        request=EmailLoginSerializer,
        responses={
            200: {
                'description':'Login Successful', 
                'content':{
                    'application/json': {
                        'example': {
                            'status': 'Success',
                            'message': 'Login successful',
                            'token': 'your_token'
                        }
                    }
                }
            },
            400: {
                'description':'Invalid Credentials or Bad Request', 
                'content':{
                    'application/json': {
                        'example': {
                            'status': 'Error',
                            'message': 'Invalid credentials'
                        },
                        'example2': {
                            'status': 'Error',
                            'message': 'This field is required.'
                        }
                    }
                }
            }
        },
        examples=[
            OpenApiExample(
                name="Successful Login",
                description="A successful login request.",
                value={
                    "email": "user@example.com",
                    "password": "securepassword123"
                },
                request_only=True  # This specifies that this example is only for request
            ),
            OpenApiExample(
                name="Failed Login",
                description="A failed login request due to invalid credentials.",
                value={
                    "email": "user@example.com",
                    "password": "wrongpassword"
                },
                request_only=True
            )
        ]
    )
    
    def post(self, request, *args, **kwargs):
        serializer = EmailLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response(
                    {
                        'status': 'Success',
                        'message': 'Login successful',
                        'token': token.key
                    }, status=status.HTTP_200_OK)
            return Response({'status': 'Error', 'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FacialRecognitionLoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        description="Authenticate a user using facial recognition.",
        request={
            'multipart/form-data': {
                'type':'object',
                'properties':{
                    'image': {
                        'type': 'string', 
                        'format': 'binary',
                        'description':'Login Face Image Uploaded by User'
                    }
                }
            }
        },
        responses={
            200: {
                'description': 'Login Successful',
                'content': {
                    'application/json': {
                        'example': {
                            'status': 'Success',
                            'message': 'Login successful',
                            'user_id': '123',
                            'token': 'your_token'
                        }
                    }
                }
            },
            400: {
                'description': 'Invalid or Missing Image',
                'content': {
                    'application/json': {
                        'examples': {
                            'invalid_image': {
                                'summary': 'Invalid Image Provided',
                                'value': {
                                    'status': 'Error',
                                    'message': 'Invalid image format or corrupted file.'
                                }
                            },
                            'no_face_detected': {
                                'summary': 'No Face Detected',
                                'value': {
                                    'status': 'Error',
                                    'message': 'No recognizable face detected in the image.'
                                }
                            }
                        }
                    }
                }
            }
        },
        examples=[
            OpenApiExample(
                name="Submit Image for Facial Recognition",
                summary="Example of submitting an image for facial recognition login.",
                description="A valid image file is submitted to be processed for facial recognition.",
                value={
                    "image": "path/to/your/image.jpg"
                },
                request_only=True
            ),
            OpenApiExample(
                name="Successful Login Response",
                summary="Successful login after facial recognition.",
                description="Response after a successful facial recognition that identifies the user.",
                value={
                    "status": "Success",
                    "message": "Login successful",
                    "user_id": "123",
                    "token": "your_token"
                },
                response_only=True
            ),
            OpenApiExample(
                name="Failed Login Response - No Face Detected",
                summary="No face detected in the image.",
                description="Response when no recognizable face is detected in the submitted image.",
                value={
                    "status": "Error",
                    "message": "No recognizable face detected in the image."
                },
                response_only=True
            )
        ]
    )

    def post(self, request, *args, **kwargs):
        from rest_framework.parsers import MultiPartParser, FormParser
        request.parser_classes = [MultiPartParser, FormParser]
        
        image_serializer = FacialRecognitionLoginSerializer(data=request.data)
        if image_serializer.is_valid():
            image_file = request.FILES.get('image')

            if image_file:
                face_match = FaceMatch(image_file)
                match_result = face_match.new_face_matching()

                if match_result['status'] == 'Success':
                    user_id = match_result['user_id']
                    try:
                        user = UserProfile.objects.get(pk=user_id)
                        token, _ = Token.objects.get_or_create(user=user)
                        return Response(
                            {
                                'status': 'Success',
                                'message': 'Login successful',
                                'user_id': user_id,
                                'token': token.key
                            }, status=status.HTTP_200_OK)
                    except UserProfile.DoesNotExist:
                        return Response({
                            'status': 'Error',
                            'message': 'User not found.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                return Response({'status': 'Error', 'message': match_result['message']}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'status': 'Error', 'message': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Retrieve the authenticated user's profile.",
        responses={
            200: UserProfileSerializer,
            404: {'description': 'Profile not found'}
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            profile = UserProfile.objects.get(pk=request.user.id)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({'status': 'Error', 'message': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        description="Update the authenticated user's profile.",
        request=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            400: {'description': 'Invalid data'}
        },
        examples=[
            OpenApiExample(
                name="Update Profile Example",
                summary="Example of a user profile update request.",
                description="A valid example showing how to update user profile data.",
                value={
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "updated@example.com",
                    "age": 30,
                    "preferences": "Updated preferences",
                },
                request_only=True
            ),
            OpenApiExample(
                name="Successful Profile Update Response",
                summary="Successful profile update response.",
                description="Response returned after successfully updating the user profile.",
                value={
                    "id": 1,
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "updated@example.com",
                    "age": 30,
                    "preferences": "Updated preferences"
                },
                response_only=True
            )
        ]
    )
    def put(self, request, *args, **kwargs):
        try:
            profile = UserProfile.objects.get(pk=request.user.id)
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return Response({'status': 'Error', 'message': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
