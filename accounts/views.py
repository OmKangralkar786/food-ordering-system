from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .decorators import admin_required, is_admin_user
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from django.utils.http import url_has_allowed_host_and_scheme

from .forms import RegisterForm
from .models import User
from .otp import (
    generate_otp,
    send_otp_email,
    store_otp_in_session,
    otp_is_valid,
    mark_email_verified,
    is_email_verified,
    can_resend_otp,
    seconds_until_resend,
)


def _normalize_email(email):
    return email.strip().lower()


@require_POST
def send_otp_view(request):
    email = _normalize_email(request.POST.get('email', ''))

    if not email:
        return JsonResponse({'success': False, 'message': 'Please enter your email address.'})

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'success': False, 'message': 'Please enter a valid email address.'})

    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({'success': False, 'message': 'This email is already registered.'})

    if not can_resend_otp(request):
        wait = seconds_until_resend(request)
        return JsonResponse({
            'success': False,
            'message': f'Please wait {wait} seconds before requesting another OTP.',
            'wait_seconds': wait,
        })

    otp = generate_otp()
    store_otp_in_session(request, email, otp)

    try:
        send_otp_email(email, otp)
    except Exception:
        return JsonResponse({
            'success': False,
            'message': 'Could not send OTP email. Please check email settings and try again.',
        })

    return JsonResponse({
        'success': True,
        'message': 'OTP sent successfully. Check your inbox.',
        'wait_seconds': 60,
    })


@require_POST
def verify_otp_view(request):
    email = _normalize_email(request.POST.get('email', ''))
    otp = request.POST.get('otp', '').strip()

    if not email or not otp:
        return JsonResponse({'success': False, 'message': 'Email and OTP are required.'})

    valid, error_message = otp_is_valid(request, email, otp)
    if not valid:
        return JsonResponse({'success': False, 'message': error_message})

    mark_email_verified(request, email)
    return JsonResponse({'success': True, 'message': 'Email verified successfully!'})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    email_verified = request.session.get('verified_email', '')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        email = _normalize_email(request.POST.get('email', ''))

        if not is_email_verified(request, email):
            form.add_error('email', 'Please verify your email with OTP before registering.')
        elif form.is_valid():
            user = form.save()
            request.session.pop('verified_email', None)
            request.session.pop('otp_email', None)
            request.session.pop('otp_sent_at', None)
            login(request, user)
            messages.success(request, 'Account created successfully. Welcome to FoodHub!')
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'email_verified': email_verified,
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            if is_admin_user(user):
                return redirect('admin_dashboard')
            return redirect('home')
        messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
@admin_required
def admin_dashboard_view(request):
    return render(request, 'accounts/admin_dashboard.html')


@login_required
@admin_required
def user_list_view(request):
    query = request.GET.get('q', '').strip()
    users = User.objects.all().order_by('-date_joined')

    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

    customer_count = users.filter(role='customer').count()
    staff_count = users.filter(is_staff=True).count()

    return render(request, 'accounts/user_list.html', {
        'users': users,
        'query': query,
        'total_count': users.count(),
        'customer_count': customer_count,
        'staff_count': staff_count,
    })


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('register')
