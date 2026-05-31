from django.urls import path

from .views import delivery_dashboard

urlpatterns = [

    path('dashboard/',
         delivery_dashboard,
         name='delivery_dashboard'),
]