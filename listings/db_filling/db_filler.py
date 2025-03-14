import os
import django
import json
import random
import base64

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FlatsKG.settings")
django.setup()

# Теперь можно импортировать модели
from listings.models import Listing, ListingDetail, ListingPicture
from users.models import User

with open(r'data/flats_kg_data.json', 'r') as file:
    flats = json.load(file)

with open(r'data/images/flats_with_images_200_.json', 'r') as file:
    images = json.load(file)


def encode_image_to_base64(image_path):
    """Функция кодирует изображение в Base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


counter = 0
user = User.objects.get(id=7)

for link, data in flats.items():
    if link not in images.keys():
        continue
    image_subdir = list(images[link].keys())[0]
    images_path = r'data/images/decoded_images/' + image_subdir
    flat_images = list()
    for flat_image in os.listdir(images_path):
        flat_images.append(images_path + r'/' + flat_image)

    room_num = int(data['room_options']) if data['room_options'][0].isdigit() else 6
    listing = Listing.objects.create(
        user=user,
        rooms=room_num,
        price=data['price'],
        address=data['address'],
    )

    listing_detail = ListingDetail.objects.create(
        listing=listing,
        listing_type=data['listing_types'],
        apartment_series=data['apartment_series'],
        heating=data['heating_options'],
        condition=data['conditions'],
        furniture=data['furniture_options'],
        area=random.randint(50, 150),
        floor=data['floor'],
        total_floors=data['total_floors'],
        year_built=data['year_built'],
        wall_material=data['wall_material_options'],
        developer=data['developers'],
        description=data['description'],
        region=data['region_options'],
        city=data['city_options']
    )

    for im in flat_images:
        ListingPicture.objects.create(
            listing=listing,
            image_base64=encode_image_to_base64(im)
        )

