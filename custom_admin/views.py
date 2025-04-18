from django.shortcuts import render


def show_admin_profile(request):
    return render(request, 'custom_admin/admin_profile.html')


from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from users.models import User


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
