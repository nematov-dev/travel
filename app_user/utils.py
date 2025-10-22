from django.core.mail import send_mail
from django.conf import settings


def send_email_code(email, code):
    """
    Foydalanuvchiga email orqali tasdiqlash kodi yuboradi.
    """
    subject = "Ro‘yxatdan o‘tish tasdiqlash kodi"
    message = f"Sizning tasdiqlash kodingiz: {code}"

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False
    )

    return True

def reset_email_code(email, code):
    """
    Foydalanuvchiga email orqali tasdiqlash kodi yuboradi.
    """
    subject = "Parolni o'zgartirish tasdiqlash kodi"
    message = f"Sizning tasdiqlash kodingiz: {code}"

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False
    )

    return True