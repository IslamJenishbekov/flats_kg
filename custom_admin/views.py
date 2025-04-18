from django.shortcuts import render

def show_admin_profile(request):
    return render(request, 'custom_admin/admin_profile.html')
