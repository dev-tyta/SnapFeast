from django.urls import path
from .views import EmailLoginView, FaceLoginView, UserSignUpAPIView, UpdateFaceView, UserProfileAPIView, CustomTokenRefreshView

urlpatterns = [
    path('signup/', UserSignUpAPIView.as_view(), name='user_signup'),
    path('login/email/', EmailLoginView.as_view(), name='email_login'),
    path('login/face/', FaceLoginView.as_view(), name='face_login'),
    path('update/face/', UpdateFaceView.as_view(), name='update_face'),
    path('update/profile/', UserProfileAPIView.as_view(), name='update_profile'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]