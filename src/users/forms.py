from typing import Any
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm

from .models import Customer


class UserSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Customer
        fields = UserCreationForm.Meta.fields + ('name', 'mail', 'age', 'profile_pic', 'preferences')   

class UserUpdateForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Customer
        fields = UserChangeForm.Meta.fields + ('name', 'mail', 'age', 'profile_pic', 'preferences')
