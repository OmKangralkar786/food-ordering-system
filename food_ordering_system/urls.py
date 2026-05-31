from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, redirect

def home(request):
    if not request.user.is_authenticated:
        return redirect('register')
    return render(request, 'home.html')

urlpatterns = [
    path('', home, name='home'),

    path('admin/', admin.site.urls),

    path('accounts/', include('accounts.urls')),

    path('restaurants/', include('restaurants.urls')),

    path('menu/', include('menu.urls')),

    path('orders/', include('orders.urls')),

    path('delivery/', include('delivery.urls')),

    path('analytics/', include('analytics_app.urls')),

    path('chat/',include('support_chat.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)