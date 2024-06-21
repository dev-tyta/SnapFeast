from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import UserProfile, UserImage, UserEmbeddings
from .forms import UserSignUpForm, UserUpdateForm, UserImage


# Register your models here.
class UserProfileAdmin(UserAdmin):
    model = UserProfile
    add_form = UserSignUpForm
    form = UserUpdateForm
    list_display = ['first_name', 'last_name', 'mail', 'age']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('age', 'preferences')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('first_name', 'last_name', 'mail', 'age', 'preferences')}),
    )

admin.site.register(UserProfile, UserProfileAdmin)


class UserImageAdmin(admin.ModelAdmin):
    form= UserImage
    list_display = ['user', 'image']
    list_filter = ['user__first_name', 'user__last_name']
    search_fields = ['user__first_name', 'user__last_name']

admin.site.register(UserImage, UserImageAdmin)


class UserEmbeddingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'embeddings']
    list_filter = ['user']
    search_fields = ['user__first_name', 'user__last_name']

    def embeddings_info(self, obj):
        return "Available" if obj.embeddings else "Not Available"

admin.site.register(UserEmbeddings, UserEmbeddingsAdmin)