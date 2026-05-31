from django.urls import path

from .views import support_chat

urlpatterns = [

    path('',
         support_chat,
         name='support_chat'),
]