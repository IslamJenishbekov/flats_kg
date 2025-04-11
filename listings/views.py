import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from listings.models import *
from moderation.models import Blocking
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
from io import BytesIO
from .services import get_predicted_price, main_chat, listing_chat
from django.contrib import messages
import io
from listings.comment_form import CommentForm
from django.core.paginator import Paginator


def show_all_listings(request):
    # Получаем параметры из GET-запроса
    listing_type = request.GET.get('listing_type', '')
    apartment_series = request.GET.get('apartment_series', '')
    rooms = request.GET.get('rooms', '')
    heating = request.GET.get('heating', '')
    condition = request.GET.get('condition', '')
    furniture = request.GET.get('furniture', '')
    region = request.GET.get('region', '')
    city = request.GET.get('city', '')
    developer = request.GET.get('developer', '')
    wall_material = request.GET.get('wall_material', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    area_min = request.GET.get('area_min', '')
    area_max = request.GET.get('area_max', '')
    floor_min = request.GET.get('floor_min', '')
    floor_max = request.GET.get('floor_max', '')

    # Базовый queryset с учетом is_blocked=False
    listings = Listing.objects.filter(is_blocked=False)

    # Фильтрация по полям модели Listing
    if rooms:
        listings = listings.filter(rooms=rooms)
    if price_min:
        listings = listings.filter(price__gte=price_min)
    if price_max:
        listings = listings.filter(price__lte=price_max)

    # Фильтрация по полям модели ListingDetail через связь
    if listing_type:
        listings = listings.filter(details__listing_type=listing_type)
    if apartment_series:
        listings = listings.filter(details__apartment_series=apartment_series)
    if heating:
        listings = listings.filter(details__heating=heating)
    if condition:
        listings = listings.filter(details__condition=condition)
    if furniture:
        listings = listings.filter(details__furniture=furniture)
    if region:
        listings = listings.filter(details__region=region)
    if city:
        listings = listings.filter(details__city=city)
    if developer:
        listings = listings.filter(details__developer=developer)
    if wall_material:
        listings = listings.filter(details__wall_material=wall_material)
    if area_min:
        listings = listings.filter(details__area__gte=area_min)
    if area_max:
        listings = listings.filter(details__area__lte=area_max)
    if floor_min:
        listings = listings.filter(details__floor__gte=floor_min)
    if floor_max:
        listings = listings.filter(details__floor__lte=floor_max)

    # Пагинация
    paginator = Paginator(listings, 10)  # Показывать 10 объявлений на странице
    page_number = request.GET.get('page')  # Получаем номер страницы из GET-запроса
    page_obj = paginator.get_page(page_number)  # Получаем объект страницы

    # Получаем список объявлений с первой картинкой только для текущей страницы
    listings_with_pictures = [
        {
            'listing': listing,
            'picture': ListingPicture.objects.filter(listing=listing).first()
        }
        for listing in page_obj  # Используем page_obj вместо listings
    ]

    # Загружаем возможные значения фильтров из JSON
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'possible_fields.json')
    with open(json_path, 'r', encoding='utf-8') as file:
        filter_values = json.load(file)

    # Передаем данные в шаблон
    return render(request, 'listings/all_listings.html', {
        'listings_with_pictures': listings_with_pictures,
        'filter_values': filter_values,
        'page_obj': page_obj,  # Передаем объект пагинации для шаблона
    })


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
    if request.method == "POST" and request.user.role == 'moderator':
        listing_id = request.POST.get('listing_id')
        reason = request.POST.get('reason')

        listing = get_object_or_404(Listing, id=listing_id)
        user = get_object_or_404(User, id=listing.user.id)

        blocking = Blocking(blocking_cause=reason, listing=listing)
        blocking.save()

        listing.is_blocked = True
        listing.save(update_fields=['is_blocked'])

        messages.success(request, "Объявление успешно заблокировано!")
        return redirect("all_listings")

    if request.method == "POST" and 'toggle_like' in request.POST:
        listing = get_object_or_404(Listing, id=listing_id)
        user = get_object_or_404(User, id=request.user.id)
        # Проверяем, что пользователь не автор
        if request.user != listing.user:
            listing_details = get_object_or_404(ListingDetail, listing_id=listing.id)
            if Favorites.objects.filter(user=user, listing=listing).exists():
                # Удаляем лайк
                listing_details.num_likes -= 1
                Favorites.objects.filter(user=user, listing=listing).delete()
            else:
                listing_details.num_likes += 1
                favorite = Favorites(user=user, listing=listing)
                favorite.save()
            listing_details.save()

    if request.user.role == "support" and request.method == "POST":
        listing = get_object_or_404(Listing, id=listing_id)
        listing.is_blocked = False
        print('unblocked')
        listing.save(update_fields=['is_blocked'])
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect to login if not authenticated
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            listing = get_object_or_404(Listing, id=listing_id)
            comment.listing = listing
            comment.user = request.user
            comment.save()
            return redirect('listing_detail', listing_id=listing_id)

    listing = get_object_or_404(Listing, id=listing_id)
    listing_details = listing.details  # Получаем связанные детали объявления
    comments = listing.comments.all().order_by('-created_at')  # Все комментарии, сортированные по дате
    pictures = listing.pictures.all()  # Все изображения объявления

    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = Favorites.objects.filter(user=request.user, listing=listing).exists()

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
    comment_form = CommentForm()
    context = {
        'listing': listing,
        'listing_details': listing_details,
        'comments': comments,
        'pictures': pictures,
        'predicted_price': predicted_price,
        'comment_form': comment_form,
        "user_has_liked": user_has_liked,
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
        data = json.loads(request.body.decode('utf-8'))
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
            'description': listing_details.description,
            'price': listing.price,
        }

        chat_response = listing_chat.get_response(message, flat_data)

        if isinstance(chat_response, str):
            return JsonResponse({'response': chat_response})

        return chat_response


def show_my_favorites(request):
    favorite_listings = Listing.objects.filter(favorites__user=request.user)
    listings_with_pictures = [
        {
            'listing': listing,
            'picture': ListingPicture.objects.filter(listing=listing).first()
        }
        for listing in favorite_listings
    ]
    return render(request, 'listings/my_favorite_listings.html', {'listings_with_pictures': listings_with_pictures})


def edit_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, user=request.user)
    listing_detail = listing.details

    if request.method == 'POST':
        # Обновляем основные поля Listing
        listing.rooms = request.POST.get('rooms')
        listing.price = request.POST.get('price')
        listing.address = request.POST.get('address')
        listing.save()

        # Обновляем поля ListingDetail
        listing_detail.listing_type = request.POST.get('listing_type')
        listing_detail.apartment_series = request.POST.get('apartment_series')
        listing_detail.heating = request.POST.get('heating')
        listing_detail.condition = request.POST.get('condition')
        listing_detail.furniture = request.POST.get('furniture')
        listing_detail.area = request.POST.get('area')
        listing_detail.floor = request.POST.get('floor')
        listing_detail.total_floors = request.POST.get('total_floors')
        listing_detail.year_built = request.POST.get('year_built')
        listing_detail.wall_material = request.POST.get('wall_material')
        listing_detail.developer = request.POST.get('developer')
        listing_detail.description = request.POST.get('description')
        listing_detail.region = request.POST.get('region')
        listing_detail.city = request.POST.get('city')
        listing_detail.save()

        # Обработка новых картинок
        if 'pictures' in request.FILES:
            for file in request.FILES.getlist('pictures'):
                # Конвертируем файл в base64
                buffered = io.BytesIO()
                file.save(buffered)
                encoded_string = base64.b64encode(buffered.getvalue()).decode('utf-8')

                ListingPicture.objects.create(
                    listing=listing,
                    image_base64=encoded_string
                )

        return redirect('listing_detail', listing_id=listing.id)  # Перенаправление после сохранения

    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'possible_fields.json')

    with open(json_path, 'r', encoding='utf-8') as file:
        context = json.load(file)

    context["pictures"] = listing.pictures.all()
    context["listing_detail"] = listing_detail
    context["listing"] = listing

    return render(request, 'listings/edit_listing.html', context)


def delete_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, user=request.user)

    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Объявление успешно удалено')
        return redirect('my_listings')

    return redirect("my_listings")


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(ListingComment, id=comment_id)
    if comment.user != request.user:
        return redirect('listing_detail', listing_id=comment.listing.id)  # Only owner can edit

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('listing_detail', listing_id=comment.listing.id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'listings/edit_comment.html', {'form': form, 'comment': comment})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(ListingComment, id=comment_id)
    if comment.user != request.user:
        return redirect('listing_detail', listing_id=comment.listing.id)  # Only owner can delete

    if request.method == 'POST':
        listing_id = comment.listing.id
        comment.delete()
        return redirect('listing_detail', listing_id=listing_id)
    else:
        return render(request, 'listings/delete_comment.html', {'comment': comment})


def show_another_user_listings(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_listings = Listing.objects.filter(user=user, is_blocked=False)
    if request.user.role == "support":
        user_listings = Listing.objects.filter(user=user)

    listings_with_pictures = [
        {
            'listing': listing,
            'picture': ListingPicture.objects.filter(listing=listing).first()
        }
        for listing in user_listings
    ]
    return render(request, 'listings/another_user_listings.html', {'listings_with_pictures': listings_with_pictures})

# TODO implement delete_picture method
