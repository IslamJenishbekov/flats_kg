from django.db import models
from users.models import User
import os


class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Связь с кастомным пользователем
    num_likes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Listing {self.id} by {self.user.username}"


class ListingDetail(models.Model):  # Переименовали PublishDetail в ListingDetail
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name='details')
    listing_type = models.CharField(max_length=50)
    apartment_series = models.CharField(max_length=50)
    heating = models.CharField(max_length=50)
    condition = models.CharField(max_length=50)
    furniture = models.CharField(max_length=50)
    rooms = models.IntegerField()
    area = models.DecimalField(max_digits=5, decimal_places=2)
    floor = models.IntegerField()
    total_floors = models.IntegerField()
    year_built = models.IntegerField()
    wall_material = models.CharField(max_length=50)
    developer = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return f"Details for Listing {self.listing.id}"


class ListingComment(models.Model):  # Переименовали PublishComment в ListingComment
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Связь с кастомным пользователем
    num_likes = models.IntegerField(default=0)
    replied_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on Listing {self.listing.id}"


class ListingPicture(models.Model):
    def listing_image_path(instance, filename):
        """Создает путь вида listings/media/listing_1/photo.jpg"""
        return os.path.join("listings/media/", f"listing_{instance.listing.id}", filename)

    listing = models.ForeignKey("Listing", on_delete=models.CASCADE, related_name="pictures")
    image = models.ImageField(upload_to=listing_image_path)

    def __str__(self):
        return f"Picture for Listing {self.listing.id}"