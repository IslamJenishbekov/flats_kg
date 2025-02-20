from django.shortcuts import render


def show_all_listings(request):
    return render(request, 'listings/all_listings.html')
