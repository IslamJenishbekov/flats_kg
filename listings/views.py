import json
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import default_storage
from listings.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
from io import BytesIO
from .services import get_predicted_price, main_chat, listing_chat


def show_all_listings(request):
    listings = Listing.objects.all()
    listings_with_pictures = [
        {
            'listing': listing,
            'picture': ListingPicture.objects.filter(listing=listing).first()
        }
        for listing in listings
    ]
    return render(request, 'listings/all_listings.html', {'listings_with_pictures': listings_with_pictures})


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
    listing = get_object_or_404(Listing, id=listing_id)
    listing_details = listing.details  # Получаем связанные детали объявления
    comments = listing.comments.all().order_by('-created_at')  # Все комментарии, сортированные по дате
    pictures = listing.pictures.all()  # Все изображения объявления

    flat_data = {
        'room_num': listing.rooms,
        'address': listing.address,
        'offer_type': listing_details.listing_type,
        'series': listing_details.apartment_series,
        'heating': listing_details.heating,
        'condition': listing_details.condition,
        'furniture': listing_details.furniture,
        'area': listing_details.area,
        'floor': listing_details.floor,
        'total_floors': listing_details.total_floors,
        'building_year': listing_details.year_built,
        'wall_material': listing_details.wall_material,
        'developer': listing_details.developer,
        'region': listing_details.region,
        'city': listing_details.city,
    }

    predicted_price = get_predicted_price.get_predicted_price(flat_data)
    context = {
        'listing': listing,
        'listing_details': listing_details,
        'comments': comments,
        'pictures': pictures,
        'predicted_price': predicted_price
    }

    return render(request, 'listings/listing_detail.html', context)


@csrf_exempt
def main_chat_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get('message', '')

        response = main_chat.get_response(message)

        return JsonResponse({'response': response})


@csrf_exempt
def listing_chat_view(request):
    if request.method == 'POST':
        data = json.loads(request)
        message = data.get('message', '')
        listing_id = data.get('listing_id', '')

        listing = get_object_or_404(Listing, id=listing_id)
        listing_details = listing.details

        flat_data = {
            'room_num': listing.rooms,
            'address': listing.address,
            'offer_type': listing_details.listing_type,
            'series': listing_details.apartment_series,
            'heating': listing_details.heating,
            'condition': listing_details.condition,
            'furniture': listing_details.furniture,
            'area': listing_details.area,
            'floor': listing_details.floor,
            'total_floors': listing_details.total_floors,
            'building_year': listing_details.year_built,
            'wall_material': listing_details.wall_material,
            'developer': listing_details.developer,
            'region': listing_details.region,
            'city': listing_details.city,
        }


        response = listing_chat.get_response(message, flat_data)

        return response