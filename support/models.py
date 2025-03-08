from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Appeal(models.Model):
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appeals")
    created_at = models.DateTimeField(auto_now_add=True)
    last_answered_at = models.DateTimeField(auto_now=True)

    closed = models.BooleanField(default=False)

    def __str__(self):
        return f"Appeal {self.id} by {self.user.username}"


class AppealPicture(models.Model):
    image_base64 = models.TextField()
    appeal = models.ForeignKey(Appeal, on_delete=models.CASCADE, related_name='pictures')

    def __str__(self):
        return f"Picture {self.id} for Appeal {self.appeal.id}"


class AppealStatus(models.Model):
    appeal = models.ForeignKey(Appeal, on_delete=models.CASCADE, related_name="appeal_status")
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now=True)