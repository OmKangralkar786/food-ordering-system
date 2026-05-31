from django.urls import path
from .views import (
    create_restaurant,
    restaurant_list,
    restaurant_detail,
    add_review,
    search_restaurants,
    restaurant_api,
    recommended_foods,
)

urlpatterns = [
    path('create/', create_restaurant, name='create_restaurant'),
    path('search/', search_restaurants, name='search_restaurants'),
    path('recommendations/', recommended_foods, name='recommendations'),
    path('review/<int:restaurant_id>/', add_review, name='add_review'),
    path('api/restaurants/', restaurant_api, name='restaurant_api'),
    path('<int:restaurant_id>/', restaurant_detail, name='restaurant_detail'),
    path('', restaurant_list, name='restaurant_list'),
]
