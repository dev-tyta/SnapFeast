from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest

class EmailBackend(ModelBackend):
    def authenticate(self, request: HttpRequest, username: str | None = ..., password: str | None = ..., **kwargs: Any):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(mail=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user

        return None
    
    def get_user(self, user_id: int) -> AbstractBaseUser | None:
        UserModel = get_user_model()

        try: 
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None