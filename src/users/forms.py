from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Customer


class CustomerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Customer
        fields = UserCreationForm.Meta.fields + ('name', 'email', 'phone', 'profile_pic')   

class CustomerChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Customer
        fields = UserChangeForm.Meta.fields
