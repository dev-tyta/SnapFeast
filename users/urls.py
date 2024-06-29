from django.urls import path
from .views import FacialRecognitionLoginAPIView, EmailLoginAPIView, UserSignUpAPIView, UserProfileAPIView

app_name = 'users' 

urlpatterns = [
    path('signup/', UserSignUpAPIView.as_view(), name='signup'),
    path('login/', EmailLoginAPIView.as_view(), name='login'),
    path('update/', UserProfileAPIView.as_view(), name='update'),
    path('facial-login/', FacialRecognitionLoginAPIView.as_view(), name='facial-login')
]
