from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Notification, UserNotificationStatus

# Admin for CustomUser model
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'first_name', 'last_name', 'email', 'is_parent','is_staff']
    list_filter = ['is_staff','is_active', 'is_parent']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']

    fieldsets = (
        (None, {'fields': ('username', 'password')}), 
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'is_parent')}),
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



@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    list_filter = ('created_at', 'is_public')
    search_fields = ('title', 'message', 'user__username')
    ordering = ('-created_at',)

@admin.register(UserNotificationStatus)
class UserNotificationStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification', 'is_read', 'read_at')
    list_filter = ('is_read', 'read_at')