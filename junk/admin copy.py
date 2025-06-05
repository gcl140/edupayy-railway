from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Admin for CustomUser model
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'first_name', 'last_name', 'email', 'is_intern','is_staff']
    list_filter = ['is_staff','is_active', 'is_intern']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']

    fieldsets = (
        (None, {'fields': ('username', 'password')}), 
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'is_intern')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'is_active', 'is_staff'),
        }),
    )

# Register CustomUser model
admin.site.register(CustomUser, CustomUserAdmin)
