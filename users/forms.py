from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UserProfile

class UserSignUpForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'email', 'age','preferences', 'password')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use.")
        return email

class UserUpdateForm(UserChangeForm):
    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'email', 'age', 'preferences')

class EmailLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
