from django.db import models
from django.contrib.auth import get_user_model
from listings.models import Listing

User = get_user_model()


class Blocking(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="blocking")
    listing = models.ForeignKey(Listing, null=True, on_delete=models.CASCADE, related_name="blocking")
    blocking_cause = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blocking {self.id}"
