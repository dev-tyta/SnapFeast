from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from .serializers import UserRegistrationSerializer, EmailLoginSerializer, FaceLoginSerializer, UserProfileSerializer
from .models import UserProfile, UserEmbeddings
from utils.facial_processing import FacialProcessing
from utils.match_face import FaceMatch


class UserSignUpAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    @extend_schema(
        tags=['Authentication'],
        operation_id='user_signup',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'description': 'Username for the new user. Must be unique.'},
                    'first_name': {'type': 'string', 'description': 'First name of the new user.'},
                    'last_name': {'type': 'string', 'description': 'Last name of the new user.'},
                    'email': {'type': 'string', 'format': 'email', 'description': 'Email address of the new user. Must be unique.'},
                    'password': {'type': 'string', 'format': 'password', 'description': 'Password for the new user.'},
                    'age': {'type': 'integer', 'description': 'Age of the new user. Must be an integer.'},
                    'preferences': {'type': 'string', 'description': 'Food Preferences of User'},
                    'image': {'type': 'string', 'format': 'binary', 'description':'Face Image Uploaded by User'},
                }
            }
        },
        responses={201: UserRegistrationSerializer, 400: {'description': 'Invalid data'}},
        description="Register a new user and their facial data for recognition.",
        examples=[
            OpenApiExample(
                "Valid Signup Request",
                summary="Example of a valid signup request",
                value={
                    "username": "john_doe",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "password": "securepassword123",
                    "age": 30,
                    "preferences": "Vegetarian",
                }
            )
        ]
    )        
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    user.set_password(request.data["password"])
                    user.save()

                    processor = FacialProcessing()
                    image = request.FILES.get("image")
                    if not image:
                        raise ValueError("Face image is required for signup")

                    results = processor.process_user_images([image], user.id)

                    if all(result['status'] == 'success' for result in results):
                        refresh = RefreshToken.for_user(user)
                        return Response({
                            'status': 'Success',
                            'message': 'User and facial data registered successfully',
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                            'user': UserProfileSerializer(user).data
                        }, status=status.HTTP_201_CREATED)
                    raise ValueError('Facial processing errors')
            except ValueError as e:
                return Response({
                    'status': 'Error',
                    'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Authentication'],
        operation_id='email_login',
        request=EmailLoginSerializer,
        responses={200: {'description': 'Login successful'}, 401: {'description': 'Invalid credentials'}},
        description="Login with email and password"
    )
    def post(self, request):
        serializer = EmailLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserProfileSerializer(user).data
                })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class FaceLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Authentication'],
        operation_id='face_login',
        request=FaceLoginSerializer,
        responses={200: {'description': 'Login successful'}, 401: {'description': 'Face not recognized'}},
        description="Login with facial recognition"
    )
    def post(self, request):
        serializer = FaceLoginSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']
            
            path = default_storage.save('tmp/face_login.jpg', ContentFile(image.read()))
            
            face_processor = FacialProcessing()
            embeddings = face_processor.extract_embeddings(path)
            
            if embeddings:
                face_matcher = FaceMatch()
                match_result = face_matcher.new_face_matching(embeddings)
                
                if match_result['status'] == 'Success':
                    user = UserProfile.objects.get(id=match_result['user_id'])
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'user': UserProfileSerializer(user).data
                    })
            
            return Response({'error': 'Face not recognized'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateFaceView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['User'],
        operation_id='update_face',
        request={'multipart/form-data': {'type': 'object', 'properties': {'image': {'type': 'string', 'format': 'binary'}}}},
        responses={200: {'description': 'Face updated successfully'}, 400: {'description': 'Failed to process face'}},
        description="Update user's facial data"
    )
    def post(self, request):
        image = request.FILES.get('image')
        if not image:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        path = default_storage.save(f'faces/{request.user.id}.jpg', ContentFile(image.read()))
        
        face_processor = FacialProcessing()
        embeddings = face_processor.extract_embeddings(path)
        
        if embeddings:
            UserEmbeddings.objects.update_or_create(
                user=request.user,
                defaults={'embeddings': embeddings}
            )
            return Response({'message': 'Face updated successfully'}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Failed to process face'}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['User'],
        operation_id='get_user_profile',
        responses={200: UserProfileSerializer, 404: {'description': 'Profile not found'}},
        description="Retrieve the authenticated user's profile."
    )
    def get(self, request, *args, **kwargs):
        try:
            profile = UserProfile.objects.get(pk=request.user.id)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({'status': 'Error', 'message': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        tags=['User'],
        operation_id='update_user_profile',
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer, 400: {'description': 'Invalid data'}},
        description="Update the authenticated user's profile.",
        examples=[
            OpenApiExample(
                name="Update Profile Example",
                summary="Example of a user profile update request.",
                value={
                    "username": "updated_username",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "updated@example.com",
                    "age": 30,
                    "preferences": "Updated preferences",
                },
                request_only=True
            ),
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