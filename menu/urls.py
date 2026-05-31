from django.urls import path
from .views import add_menu_item, menu_list, favorites, add_to_favorites

urlpatterns = [
    path('add/', add_menu_item, name='add_menu_item'),
    path('', menu_list, name='menu_list'),
    path('favorites/',favorites,name='favorites'),
    path('favorite/add/<int:item_id>/',add_to_favorites,name='add_to_favorites'),
]