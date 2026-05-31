from django.urls import path
from .views import (
    register_view,
    login_view,
    logout_view,
    send_otp_view,
    verify_otp_view,
    admin_dashboard_view,
    user_list_view,
)

urlpatterns = [
    path('register/', register_view, name='register'),
    path('send-otp/', send_otp_view, name='send_otp'),
    path('verify-otp/', verify_otp_view, name='verify_otp'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('users/', user_list_view, name='user_list'),
]
