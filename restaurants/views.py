from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_required
from .models import Restaurant, Review
from django.db.models import Q
from .forms import RestaurantForm, ReviewForm



from rest_framework.decorators import api_view

from rest_framework.response import Response

from .serializers import RestaurantSerializer



from django.db.models import Count

from menu.models import MenuItem

def recommended_foods(request):

    popular_items = MenuItem.objects.annotate(

        total_orders=Count('orderitem')

    ).order_by('-total_orders')[:6]

    return render(request,

                  'restaurants/recommendations.html',

                  {
                      'popular_items': popular_items
                  })

def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu_items = MenuItem.objects.filter(restaurant=restaurant, available=True)
    reviews = Review.objects.filter(restaurant=restaurant).order_by('-created_at')
    return render(request, 'restaurants/restaurant_detail.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
        'reviews': reviews,
    })


@login_required
def add_review(request, restaurant_id):

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == 'POST':

        form = ReviewForm(request.POST)

        if form.is_valid():

            review = form.save(commit=False)

            review.user = request.user

            review.restaurant = restaurant

            review.save()

            return redirect('restaurant_detail', restaurant_id=restaurant.id)

    else:
        form = ReviewForm()

    return render(request,
                  'restaurants/add_review.html',
                  {'form': form})
@admin_required
def create_restaurant(request):

    if request.method == 'POST':

        form = RestaurantForm(request.POST, request.FILES)

        if form.is_valid():

            restaurant = form.save(commit=False)
            restaurant.owner = request.user
            restaurant.save()

            return redirect('home')

    else:
        form = RestaurantForm()

    return render(request, 'restaurants/create_restaurant.html', {'form': form})


def restaurant_list(request):

    restaurants = Restaurant.objects.all()

    return render(request, 'restaurants/restaurant_list.html', {
        'restaurants': restaurants
    })


def search_restaurants(request):

    query = request.GET.get('q')

    cuisine = request.GET.get('cuisine')

    restaurants = Restaurant.objects.all()

    if query:

        restaurants = restaurants.filter(

            Q(name__icontains=query) |

            Q(cuisine__icontains=query)

        )

    if cuisine:

        restaurants = restaurants.filter(
            cuisine__icontains=cuisine
        )

    return render(request,
                  'restaurants/search_results.html',
                  {
                      'restaurants': restaurants,
                      'query': query or '',
                  })



@api_view(['GET'])

def restaurant_api(request):

    restaurants = Restaurant.objects.all()

    serializer = RestaurantSerializer(
        restaurants,
        many=True
    )

    return Response(serializer.data)