import json
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from listings.models import *
import base64
from io import BytesIO


def show_all_listings(request):
    return render(request, 'listings/all_listings.html')


def create_listing(request):
    if request.method == "POST":
        # Получаем данные из формы
        listing_type = request.POST.get("listing_type")
        apartment_series = request.POST.get("apartment_series")
        heating = request.POST.get("heating")
        condition = request.POST.get("condition")
        furniture = request.POST.get("furniture")
        rooms = request.POST.get("rooms")
        area = request.POST.get("area")
        floor = request.POST.get("floor")
        total_floors = request.POST.get("total_floors")
        year_built = request.POST.get("year_built")
        wall_material = request.POST.get("wall_material")
        developer = request.POST.get("developer")
        description = request.POST.get("description")
        price = request.POST.get("price")
        address = request.POST.get("address")
        region = request.POST.get("region")
        city = request.POST.get("city")

        # Создаем основную запись Listing
        listing = Listing.objects.create(user=request.user, rooms=rooms, price=price, address=address)

        # Создаем детали объявления
        ListingDetail.objects.create(
            listing=listing,
            listing_type=listing_type,
            apartment_series=apartment_series,
            heating=heating,
            condition=condition,
            furniture=furniture,
            area=area,
            floor=floor,
            total_floors=total_floors,
            year_built=year_built,
            wall_material=wall_material,
            developer=developer,
            description=description,
            region=region,
            city=city,
        )

        for image in request.FILES.getlist("pictures"):
            if isinstance(image, str):  # Если изображение уже передано в виде строки Base64
                ListingPicture.objects.create(listing=listing, image_base64=image)
            else:
                image_data = image.read()  # Читаем содержимое файла
                base64_image = base64.b64encode(image_data).decode('utf-8')  # Преобразуем в base64 строку

                ListingPicture.objects.create(listing=listing, image_base64=base64_image)

        return redirect("users:profile")

    with open(r'listings/possible_fields.json', 'r', encoding='utf-8') as file:
        context = json.load(file)
    return render(request, 'listings/create_listing.html', context)


def show_my_listings(request):
    user_listings = Listing.objects.filter(user=request.user)
    listings_with_pictures = [
        {
            'listing': listing,
            'picture': ListingPicture.objects.filter(listing=listing).first()
        }
        for listing in user_listings
    ]
    return render(request, 'listings/my_listings.html', {'listings_with_pictures': listings_with_pictures})


def show_listing_detail(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    print(listing)
    return render(request, 'listings/listing_detail.html')
