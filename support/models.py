from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Appeal(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appeals")

    def __str__(self):
        return f"Appeal {self.id} by {self.user.username}"


class AppealPicture(models.Model):
    id = models.AutoField(primary_key=True)
    image_base64 = models.TextField()
    appeal = models.ForeignKey(Appeal, on_delete=models.CASCADE, related_name='pictures')

    def __str__(self):
        return f"Picture {self.id} for Appeal {self.appeal.id}"
