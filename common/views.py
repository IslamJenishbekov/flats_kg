from django.shortcuts import render

def tell_about(request):
    return render(request, 'common/about.html')
