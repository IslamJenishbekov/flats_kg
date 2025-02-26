import json
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from listings.models import *


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

        # Создаем основную запись Listing
        listing = Listing.objects.create(user=request.user)

        # Создаем детали объявления
        ListingDetail.objects.create(
            listing=listing,
            listing_type=listing_type,
            apartment_series=apartment_series,
            heating=heating,
            condition=condition,
            furniture=furniture,
            rooms=rooms,
            area=area,
            floor=floor,
            total_floors=total_floors,
            year_built=year_built,
            wall_material=wall_material,
            developer=developer,
            description=description
        )

        # Обрабатываем загруженные изображения
        for image in request.FILES.getlist("pictures"):
            ListingPicture.objects.create(listing=listing, image=image)

        return redirect("users:profile")

    with open(r'listings/possible_fields.json', 'r') as file:
        context = json.load(file)
    return render(request, 'listings/create_listing.html', context)
