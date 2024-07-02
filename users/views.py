from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from drf_spectacular import openapi
from django.db import transaction
from django.contrib.auth import login, authenticate
from utils.match_face import FaceMatch
from utils.facial_processing import FacialProcessing
from .models import UserProfile
from .forms import EmailLoginForm, ImageUploadForm
from .serializers import UserProfileSerializer, UserImageSerializer, EmailLoginSerializer, FacialRecognitionLoginSerializer


class UserSignUpAPIView(APIView):
    @extend_schema(
        request=UserProfileSerializer,
        responses={201: UserProfileSerializer},
        description="Register a new user and their facial data for recognition.",
        parameters=[
            OpenApiParameter(
                name='image', 
                description='Upload user image', 
                required=True, 
                type=OpenApiTypes.BINARY, 
            ),
        ],
        examples=[
            OpenApiExample(
                "Example 1",
                summary="Example of a valid request",
                description="This is what a valid request might look like",
                value={
                    "username": "john_doe",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "age": 30,
                    "preferences": "None",
                    "image": "file.png"
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

                    # Assuming your UserImageSerializer saves the image and links it to the user
                    processor = FacialProcessing()
                    image_url = user.image.image.url  # Adjust based on your model structure
                    results = processor.process_user_images([image_url], user.id)

                    if all(result['status'] == 'success' for result in results):
                        return Response({
                            'status': 'Success',
                            'message': 'User and facial data registered successfully',
                            'details': results
                        }, status=status.HTTP_201_CREATED)
                    raise Exception('Facial processing errors')
            except Exception as e:
                return Response({
                    'status': 'Error',
                    'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailLoginAPIView(APIView):
    @extend_schema(
        description="Authenticate a user using their email and password.",
        request=EmailLoginSerializer,
        responses={
            200: {
                'desrciption':'Login Successful', 
                'content':{
                'application/json': {
                    'example': {
                        'status': 'Success',
                        'message': 'Login successful'
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
        form = EmailLoginForm(request.data)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return Response({'status': 'Success', 'message': 'Login successful'}, status=status.HTTP_200_OK)
            return Response({'status': 'Error', 'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class FacialRecognitionLoginAPIView(APIView):
    @extend_schema(
        description="Authenticate a user using facial recognition.",
        request=FacialRecognitionLoginSerializer,
        responses={
            200: {
                'description': 'Login Successful',
                'content': {
                    'application/json': {
                        'example': {
                            'status': 'Success',
                            'message': 'Login successful',
                            'user_id': '123'
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
        parameters=[
            OpenApiParameter(
                name='image', 
                description='Upload user image', 
                required=True, 
                type=OpenApiTypes.BINARY,
            ),
        ],
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
                    "user_id": "123"
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
        image_serializer = UserImageSerializer(data=request.data)
        if image_serializer.is_valid():
            image_instance = image_serializer.save(commit=False)
            image_file = request.FILES.get('image')

            if image_file:
                face_match = FaceMatch(image_file)
                match_result = face_match.new_face_matching()

                if match_result['status'] == 'Success':
                    user_id = match_result['user_id']
                    user = UserProfile.objects.get(pk=user_id)
                    login(request, user)
                    return Response({'status': 'Success', 'message': 'Login successful', 'user_id': user_id}, status=status.HTTP_200_OK)
                return Response({'status': 'Error', 'message': match_result['message']}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'status': 'Error', 'message': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(APIView):
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
                    "username": "updated_username",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "updated@example.com",
                    "age": 30,
                    "preferences": "Updated preferences"
                },
                request_only=True
            ),
            OpenApiExample(
                name="Successful Profile Update Response",
                summary="Successful profile update response.",
                description="Response returned after successfully updating the user profile.",
                value={
                    "id": 1,
                    "username": "updated_username",
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

