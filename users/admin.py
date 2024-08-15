from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import UserProfile, UserEmbeddings

@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'age', 'image_preview', 'is_active')
    list_filter = ('is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'age', 'preferences', 'image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'age', 'preferences', 'image'),
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'

@admin.register(UserEmbeddings)
class UserEmbeddingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'embeddings_info')
    search_fields = ('user__username', 'user__email')

    def embeddings_info(self, obj):
        return "Available" if obj.embeddings else "Not Available"
    embeddings_info.short_description = 'Embeddings Status'