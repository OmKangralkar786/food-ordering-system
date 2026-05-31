from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_required
from .forms import MenuItemForm
from .models import MenuItem, Favorite


@admin_required
def add_menu_item(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = MenuItemForm()

    return render(request, 'menu/add_menu_item.html', {'form': form})


def menu_list(request):
    items = MenuItem.objects.select_related('restaurant').filter(available=True)
    return render(request, 'menu/menu_list.html', {'items': items})


@login_required
def add_to_favorites(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    Favorite.objects.get_or_create(user=request.user, menu_item=item)
    return redirect('favorites')


@login_required
def favorites(request):
    favorite_items = Favorite.objects.filter(
        user=request.user
    ).select_related('menu_item', 'menu_item__restaurant')
    return render(request, 'menu/favorites.html', {
        'favorite_items': favorite_items
    })
