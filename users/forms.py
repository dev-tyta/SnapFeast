from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm

from .models import UserProfile, UserImage


class UserSignUpForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ('username', 'first_name', 'last_name', 'mail', 'age', 'preferences', 'password')  

class UserUpdateForm(UserChangeForm):
    class Meta:
        model = UserProfile
        fields = ('username', 'first_name', 'last_name', 'mail', 'age', 'preferences', 'password') 


class EmailLoginForm(AuthenticationForm):
    mail = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'autofocus': True}))


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UserImage
        fields = ['image']

    def __init__(self, *args, **kwargs):
        super(ImageUploadForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = False