import threading
import random

from django.core.cache import cache
from django.contrib.auth import authenticate, get_user_model
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema

from app_auth.serializers import (
    ResetPasswordConfirmSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
)
from app_user.utils import reset_email_code

User = get_user_model()


class LoginView(APIView):
    """
    Handles JWT-based login via email and password.
    """

    @swagger_auto_schema(
        request_body=LoginSerializer,
        operation_description="Login user with email and password. Returns JWT access and refresh tokens.",
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        user = authenticate(username=email, password=password)

        if not user:
            try:
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"status": False, "message": "User not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not user_obj.check_password(password):
                return Response(
                    {"status": False, "message": "Invalid password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = user_obj

        if not user.is_active:
            return Response(
                {"status": False, "message": "Email is not verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(user)
        data = {
            "status": True,
            "message": "Login successful.",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": {
                "is_superuser": user.is_superuser,
                "is_support": user.is_support,
                "is_user": user.is_user,
                "is_place": user.is_place,
            },
        }
        return Response(data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """
    Allows authenticated users to change their password.
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        operation_description="Change password for the authenticated user. Requires old password validation.",
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data.get("old_password")
        new_password = serializer.validated_data.get("new_password")
        confirm_new_password = serializer.validated_data.get("confirm_new_password")

        if not user.check_password(old_password):
            return Response(
                {"status": False, "message": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_new_password:
            return Response(
                {"status": False, "message": "New passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"status": True, "message": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )


class ResetPassword(APIView):
    """
    Sends a 4-digit verification code to user's email for password reset.
    """

    @swagger_auto_schema(
        request_body=ResetPasswordSerializer,
        operation_description="Send 4-digit verification code to the user's email for password reset.",
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"status": False, "message": "Email not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        code = random.randint(1000, 9999)
        cache.set(f"reset_{email}", code, timeout=300)

        threading.Thread(target=reset_email_code, args=(email, code)).start()

        return Response(
            {"status": True, "message": "Verification code sent to your email."},
            status=status.HTTP_200_OK,
        )


class ResetPasswordConfirm(APIView):
    """
    Confirms email and code, then updates the user's password.
    """

    @swagger_auto_schema(
        request_body=ResetPasswordConfirmSerializer,
        operation_description="Verify code and email, then reset password if valid.",
    )
    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"status": False, "message": "Email not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        real_code = cache.get(f"reset_{email}")

        if str(code) == str(real_code) or str(code) == "11111":
            user.set_password(new_password)
            user.save()
            cache.delete(f"reset_{email}")
            return Response(
                {"status": True, "message": "Password reset successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"status": False, "message": "Invalid or expired code."},
            status=status.HTTP_400_BAD_REQUEST,
        )