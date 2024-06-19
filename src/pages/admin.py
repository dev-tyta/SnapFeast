from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Customer
from .forms import CustomerCreationForm, CustomerChangeForm

# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name',
                    'email',
                    'phone',
                    'profile_pic',
                    'date_created'
                    ]
    add_form = CustomerCreationForm
    form = CustomerChangeForm
    model = Customer
    