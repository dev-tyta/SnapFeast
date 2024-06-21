from django.urls import path
from .views import FacialRecognitionLoginAPIView, UserMailLoginAPIView, UserSignUpAPIView, UserProfileUpdateAPIView

url_patterns = [
    path('signup/', UserSignUpAPIView.as_view(), name='signup'),
    path('login/', UserMailLoginAPIView.as_view(), name='login'),
    path('update/', UserProfileUpdateAPIView.as_view(), name='update'),
    path('facial-login/', FacialRecognitionLoginAPIView.as_view(), name='facial-login')
]