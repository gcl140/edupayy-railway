from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Official Email")
    username = models.EmailField(unique=True, blank=True, null=True)  # Use email as the username
    phone_number = PhoneNumberField(blank=True, null=True)
    USER_TYPE_CHOICES = [
        ('Student', 'Student'),
        ('Parent', 'Parent'),
    ]
    # user_type = models.CharField(max_length=20, default='Student', blank=True, null=True)  # Add the internship field
    is_parent = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

User = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
        help_text="Target user for the notification. Leave blank for public announcements."
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_public = models.BooleanField(default=False, help_text="Public announcements visible to all users.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        recipient = self.user.get_full_name() if self.user else "All Users"
        return f"{self.title} → {recipient}"


class UserNotificationStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_statuses')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='statuses')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'notification')
        verbose_name = "User Notification Status"
        verbose_name_plural = "User  Notification Statuses"
    
    def __str__(self):
        return f"{self.user.username} - {self.notification.title} ({'Read' if self.is_read else 'Unread'})"
