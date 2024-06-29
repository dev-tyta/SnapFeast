from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.contrib.auth import login, authenticate
from utils.match_face import FaceMatch
from utils.facial_processing import FacialProcessing
from .models import UserProfile
from .forms import EmailLoginForm, ImageUploadForm
from .serializers import UserProfileSerializer, UserImageSerializer


class UserSignUpAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user_serializer = UserProfileSerializer(data=request.data)
        image_form = ImageUploadForm(request.data, request.FILES)

        if user_serializer.is_valid() and image_form.is_valid():
            try:
                with transaction.atomic():
                    user = user_serializer.save()
                    image_instance = image_form.save(commit=False)
                    image_instance.user = user
                    image_instance.save()

                    processor = FacialProcessing()
                    results = processor.process_user_images([image_instance.image.url], user.id)

                    if all(result['status'] == 'success' for result in results):
                        return Response({'status': 'Success', 'message': 'User and facial data registered successfully', 'details': results}, status=status.HTTP_201_CREATED)
                    raise Exception('Facial processing errors')
            except Exception as e:
                return Response({'status': 'Error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            errors = {**user_serializer.errors, **image_form.errors}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        

class EmailLoginAPIView(APIView):
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

    def get(self, request, *args, **kwargs):
        profile = UserProfile.objects.get(pk=request.user.id)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        profile = UserProfile.objects.get(pk=request.user.id)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'Success', 'message': 'Profile updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
