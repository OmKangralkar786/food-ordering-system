import random
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

OTP_EXPIRY_MINUTES = 10
OTP_RESEND_SECONDS = 60


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp):
    send_mail(
        subject='FoodHub - Email Verification OTP',
        message=(
            f'Your FoodHub verification code is: {otp}\n\n'
            f'This code expires in {OTP_EXPIRY_MINUTES} minutes.\n'
            f'If you did not request this, please ignore this email.'
        ),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )


def store_otp_in_session(request, email, otp):
    request.session['otp_email'] = email
    request.session['otp_code'] = otp
    request.session['otp_expires_at'] = (
        timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    ).timestamp()
    request.session['otp_sent_at'] = timezone.now().timestamp()
    if request.session.get('verified_email') != email:
        request.session.pop('verified_email', None)


def otp_is_valid(request, email, otp):
    session_email = request.session.get('otp_email')
    session_otp = request.session.get('otp_code')
    expires_at = request.session.get('otp_expires_at')

    if not session_email or not session_otp or not expires_at:
        return False, 'Please request an OTP first.'

    if session_email != email:
        return False, 'Email does not match the OTP that was sent.'

    if timezone.now().timestamp() > expires_at:
        return False, 'OTP has expired. Please request a new one.'

    if session_otp != otp:
        return False, 'Invalid OTP. Please try again.'

    return True, ''


def mark_email_verified(request, email):
    request.session['verified_email'] = email
    request.session.pop('otp_code', None)
    request.session.pop('otp_expires_at', None)


def is_email_verified(request, email):
    return request.session.get('verified_email') == email


def can_resend_otp(request):
    sent_at = request.session.get('otp_sent_at')
    if not sent_at:
        return True
    return (timezone.now().timestamp() - sent_at) >= OTP_RESEND_SECONDS


def seconds_until_resend(request):
    sent_at = request.session.get('otp_sent_at')
    if not sent_at:
        return 0
    remaining = OTP_RESEND_SECONDS - (timezone.now().timestamp() - sent_at)
    return max(0, int(remaining))
