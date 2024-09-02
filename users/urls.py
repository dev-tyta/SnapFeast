from django.urls import path
from .views import FacialRecognitionLoginAPIView, EmailLoginAPIView, UserSignUpAPIView, UserProfileAPIView, UserEmbeddingsSetupView

app_name = 'users' 

urlpatterns = [
    path('signup/', UserSignUpAPIView.as_view(), name='signup'),
    path('login/', EmailLoginAPIView.as_view(), name='login'),
    path('signup-face/', UserEmbeddingsSetupView.as_view(), name='signup-face'),
    path('update/', UserProfileAPIView.as_view(), name='update'),
    path('facial-login/', FacialRecognitionLoginAPIView.as_view(), name='facial-login')
]
