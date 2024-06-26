from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated  
from django.core.files.base import ContentFile
from django.contrib.auth import login, authenticate
from utils.match_face import FaceMatch
from utils.facial_processing import FacialProcessing
from base64 import b64decode
from .forms import UserSignUpForm, EmailLoginForm, UserUpdateForm, ImageUploadForm



class UserSignUpAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user_form = UserSignUpForm(request.data)
        image_form = ImageUploadForm(request.data, request.FILES) 
        if user_form.is_valid() and image_form.is_valid():
            user = user_form.save()
            image_instance = image_form.save(commit=False)
            image_instance.user = user
            image_instance.save()

            processor = FacialProcessing()
            results = processor.process_user_images(image_urls=[image_instance.image.url], user_id=user.id)

            if all(result['status'] == 'success' for result in results):
                return Response({'status': 'Success', 'message': 'User and facial data registered successfully', 'details': results}, status=status.HTTP_201_CREATED)
            else:
                return Response({'status': 'Error', 'message': 'Facial processing errors', 'details': results}, status=status.HTTP_400_BAD_REQUEST)
        else:
            errors = {**user_form.errors, **image_form.errors}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        

class UserMailLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        form = EmailLoginForm(request.data)
        if form.is_valid():
            mail = form.cleaned_data['mail']
            password = form.cleaned_data['password']
            user = authenticate(request, mail=mail, password=password)
            if user is not None:
                login(request, user)
                return Response({'status': 'Success', 'message': 'User logged in successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'error', 'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        

class UserProfileUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        form = UserUpdateForm(request.data, instance=user)
        if form.is_valid():
            form.save()
            return Response({'status': 'Success', 'message': 'User profile updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        

class FacialRecognitionLoginAPIView(APIView):
    def post(self, request):
        image_data = request.data.get("image")
        if image_data:
            try:
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                image_file = ContentFile(b64decode(imgstr), name='temp.' + ext)

                match_face = FaceMatch(image_file=image_file) 
                result = match_face.new_face_matching()

                return Response(result)
            except ValueError:
                return Response({'status': 'Error', 'message': 'Image data format error'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'error', 'message': 'No image data found'}, status=status.HTTP_400_BAD_REQUEST)
        