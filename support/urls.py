from django.urls import path
from .views import *


urlpatterns = [
    path('', support, name='support'),
    path('appeals/', show_appeals, name='appeals'),
    path('appeal_<int:appeal_id>/', work_with_appeal, name='work_with_appeal')
]
