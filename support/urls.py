from django.urls import path
from .views import *


urlpatterns = [
    path('', support, name='support'),
    path('appeals/', show_appeals, name='appeals')
]
