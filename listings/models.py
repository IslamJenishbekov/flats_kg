from django.db import models
from users.models import User
import os


class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Связь с кастомным пользователем
    rooms = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=500)
    num_likes = models.IntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
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
    area = models.DecimalField(max_digits=5, decimal_places=2)
    floor = models.IntegerField()
    total_floors = models.IntegerField()
    year_built = models.IntegerField()
    wall_material = models.CharField(max_length=50)
    developer = models.CharField(max_length=50)
    description = models.TextField()
    num_likes = models.IntegerField(default=0)
    region = models.CharField()
    city = models.CharField()

    def __str__(self):
        return f"Details for Listing {self.listing.id}"


class ListingComment(models.Model):  # Переименовали PublishComment в ListingComment
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Связь с кастомным пользователем
    replied_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on Listing {self.listing.id}"


class ListingPicture(models.Model):
    listing = models.ForeignKey("Listing", on_delete=models.CASCADE, related_name="pictures")
    image_base64 = models.TextField()  # Сохраняем Base64 строку изображения

    def __str__(self):
        return f"Picture for Listing {self.listing.id}"


class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorites')


