from django.db import models
from django.contrib.auth.models import User
# from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid

class PasswordReset(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"
    
    class Meta:
        app_label = 'detector'

class Workspace(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='workspaces', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-id']

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_image = models.URLField(max_length=200, blank=True, null=True)
    role = models.CharField(
        max_length=50,
        choices=[('admin', 'Admin'), ('user', 'User')],
        default='user'
    )
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username} - {self.role} ({self.status})"

    def get_profile_image(self):
        return self.profile_image

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'Message from {self.sender} to {self.receiver}'

class Log(models.Model):
    CATEGORY_CHOICES = [
        ('DEVICE', 'Device Logs'),
        ('ACTIVITY', 'Activity Logs'),
        ('SYSTEM', 'System Logs'),
        ('USER', 'User logs'),
        ('SECURITY', 'Security Events'),
        ('NOTIFY', 'Notification Logs'),
    ]

    LEVEL_CHOICES = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('DEBUG', 'Debug'),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    message = models.TextField()
    source = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.level} - {self.timestamp}"

class CropRecommendation(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='crop_recommendations')
    nitrogen = models.FloatField()
    phosphorus = models.FloatField()
    potassium = models.FloatField()
    temperature = models.FloatField()
    moisture = models.FloatField()
    ph = models.FloatField()
    conductivity = models.FloatField()
    recommended_crop = models.CharField(max_length=100)
    confidence = models.FloatField()
    all_recommendations = models.JSONField(default=list)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.recommended_crop} ({self.confidence}%) - {self.workspace.name}"
        