from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from users.models import User
from listings.models import *

from django.db.models import Count
from django.db.models.functions import TruncDate
from datetime import timedelta
from django.utils import timezone


def show_admin_profile(request):
    # Существующие вычисления
    users_gen_num = User.objects.count()
    number_blocked_users = User.objects.filter(is_blocked=True).count()
    number_active_users = User.objects.filter(is_blocked=False).count()
    seller_count = Listing.objects.filter(is_blocked=False).values('user').distinct().count()

    listings_gen_num = Listing.objects.count()
    number_blocked_listings = Listing.objects.filter(is_blocked=True).count()
    number_active_listings = Listing.objects.filter(is_blocked=False).count()

    new_users_data = (
        User.objects
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    new_listings_data = (
        Listing.objects
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    dates = [(start_date + timedelta(days=x)).strftime('%Y-%m-%d') for x in range(31)]

    users_counts = {str(item['date']): item['count'] for item in new_users_data}
    listings_counts = {str(item['date']): item['count'] for item in new_listings_data}

    new_users_chart_data = [users_counts.get(date, 0) for date in dates]
    new_listings_chart_data = [listings_counts.get(date, 0) for date in dates]
    print(new_users_chart_data)
    print(new_listings_chart_data)

    context = {
        'users_gen_num': users_gen_num,
        'number_blocked_users': number_blocked_users,
        'number_active_users': number_active_users,
        'seller_count': seller_count,
        'listings_gen_num': listings_gen_num,
        'number_blocked_listings': number_blocked_listings,
        'number_active_listings': number_active_listings,
        'new_users_chart_data': new_users_chart_data,
        'new_listings_chart_data': new_listings_chart_data,
        'chart_dates': dates,
    }
    return render(request, 'custom_admin/admin_profile.html', context=context)


@staff_member_required
def manage_user_role(request):
    user_obj = None
    error_message = None
    success_message = None
    username = request.GET.get('username', '')

    # Handle GET request (search for user)
    if username:
        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            error_message = f"User '{username}' not found."

    # Handle POST request (update role)
    if request.method == 'POST':
        username = request.POST.get('username', username)
        role = request.POST.get('role', '').strip()
        try:
            user_obj = User.objects.get(username=username)
            if role:
                user_obj.role = role[:50]  # Ensure role doesn't exceed max_length
                user_obj.save()
                success_message = f"Role for '{username}' updated to '{role}'."
            else:
                error_message = "Role cannot be empty."
        except User.DoesNotExist:
            error_message = f"User '{username}' not found."

    return render(request, 'custom_admin/set_roles.html', {
        'user_obj': user_obj,
        'username': username,
        'error_message': error_message,
        'success_message': success_message,
    })


@staff_member_required
def manage_filters(request):
    context = {}
    for ob in FeatureOptions.objects.all():
        if ob.feature_name in context:
            context[ob.feature_name].append(ob.option)
        else:
            context[ob.feature_name] = [ob.option]

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            feature_name_select = request.POST.get('feature_name_select')
            new_feature_name = request.POST.get('new_feature_name')
            option = request.POST.get('option')

            # Определяем, какое имя фильтра использовать
            feature_name = new_feature_name if feature_name_select == 'other' and new_feature_name else feature_name_select

            if feature_name and option:
                FeatureOptions.objects.create(feature_name=feature_name, option=option)
                messages.success(request, 'Фильтр успешно добавлен!')
            else:
                messages.error(request, 'Заполните все обязательные поля!')
            return redirect('custom_admin:manage_filters')
        elif action == 'delete':
            feature_name = request.POST.get('feature_name')
            option = request.POST.get('option')
            FeatureOptions.objects.filter(feature_name=feature_name, option=option).delete()
            messages.success(request, 'Фильтр успешно удален!')
            return redirect('custom_admin:manage_filters')

    return render(request, 'custom_admin/manage_filters.html', {'filters': context})
