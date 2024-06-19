from typing import Any
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm

from .models import Customer


class UserSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Customer
        fields = UserCreationForm.Meta.fields + ('name', 'email', 'age', 'profile_pic', 'preferences')   

class UserUpdateForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Customer
        fields = UserChangeForm.Meta.fields + ('name', 'email', 'age', 'profile_pic', 'preferences')

class UserLoginForm(AuthenticationForm):
    class Meta:
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__( *args, **kwargs)
        self.fields['username'].label = 'Email'
        self.fields['password'].label = 'Password'
