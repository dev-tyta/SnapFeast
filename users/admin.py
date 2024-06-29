from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, UserImage, UserEmbeddings
from .forms import UserSignUpForm, UserUpdateForm, ImageUploadForm

@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    model = UserProfile
    add_form = UserSignUpForm
    form = UserUpdateForm
    list_display = ('first_name', 'last_name', 'email', 'age', 'is_active')
    list_filter = ('is_active', 'date_joined')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('age', 'preferences')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('first_name', 'last_name', 'email', 'age', 'preferences')}),
    )
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(UserImage)
class UserImageAdmin(admin.ModelAdmin):
    form = ImageUploadForm
    list_display = ('user', 'image')
    list_filter = ('user__first_name', 'user__last_name')
    search_fields = ('user__first_name', 'user__last_name')

@admin.register(UserEmbeddings)
class UserEmbeddingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'embeddings')
    list_filter = ('user',)
    search_fields = ('user__first_name', 'user__last_name')

    def embeddings_info(self, obj):
        return "Available" if obj.embeddings else "Not Available"
