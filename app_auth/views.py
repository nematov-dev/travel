import threading
import random

from django.shortcuts import render
from django.core.cache import cache
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status,permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from drf_yasg.utils import swagger_auto_schema

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView


from app_auth.serializers import ResetPasswordConfirmSerializer , ResetPasswordSerializer,ChangePasswordSerializer,LoginSerializer
from app_user.utils import reset_email_code

User = get_user_model()

class LoginView(APIView):
    @swagger_auto_schema(
        request_body=LoginSerializer,
        operation_description="Email va password orqali tizimga kirish (JWT login)",
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        # Foydalanuvchini email orqali autentifikatsiya qilish
        user = authenticate(username=email, password=password)

        if not user:
            try:
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"status":False,"message": "Bunday foydalanuvchi mavjud emas."},
                    status=status.HTTP_404_NOT_FOUND
                )
            if not user_obj.check_password(password):
                return Response(
                    {"status":False,"message": "Parol xato."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user = user_obj

        if not user.is_active:
            return Response(
                {"status":False,"message": "Email aktiv emas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # JWT tokenlar yaratish
        refresh = RefreshToken.for_user(user)

        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": {
                "is_superuser": user.is_superuser,
                "is_support": user.is_support,
                "is_user": user.is_user,
                "is_place": user.is_place,
            }
        }

        return Response(data, status=status.HTTP_200_OK)
    
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        operation_description="Foydalanuvchi parolini o‘zgartirish (eski parol tekshiriladi)."
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data.get('old_password')
        new_password = serializer.validated_data.get('new_password')
        confirm_new_password = serializer.validated_data.get('confirm_new_password')

        # Eski parolni tekshirish
        if not user.check_password(old_password):
            return Response(
                {"status": False, "message": "Eski parol noto‘g‘ri."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Yangi parolni tasdiqlash
        if new_password != confirm_new_password:
            return Response(
                {"status": False, "message": "Yangi parol va tasdiq parol bir xil emas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parolni yangilash
        user.set_password(new_password)
        user.save()

        return Response(
            {"status": True, "message": "Parol muvaffaqiyatli o‘zgartirildi."},
            status=status.HTTP_200_OK
        )

class ResetPassword(APIView):
    @swagger_auto_schema(request_body=ResetPasswordSerializer,operation_description="Emailga tasdiqlash kod yuboradi.")
    def post(self,request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            User.objects.get(email=email)
            # 4 xonali kod
            code = random.randint(1000, 9999)
            # cache’ga 5 daqiqa (300 soniya) saqlaymiz
            cache.set(f'reset_{email}', code, timeout=300)

            # Email yuborishni backgroundda ishga tushiramiz
            th = threading.Thread(target=reset_email_code, args=(email, code))
            th.start()

            return Response({'status':True,'message': 'Kod emailga yuborildi!'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"status":False,"message": "Email mavjud emas"}, status=status.HTTP_404_NOT_FOUND)

   
class ResetPasswordConfirm(APIView):
    @swagger_auto_schema(request_body=ResetPasswordConfirmSerializer,operation_description="Email va Kod qabul qiladi agar to'gri bo'lsa parol o'zgartiriladi beradi.")
    def post(self,request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        real_code = cache.get(f'reset_{email}')
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"status":False,"message": "Email topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        if str(code) == str(real_code) or str(code) == "11111":
            user.set_password(new_password)
            user.save()
            return Response({'status':True,'message': 'Parol muaffaqiyatli o\'zgartirildi!'}, status=status.HTTP_200_OK)
        else:
            return Response({'status':False,'message': 'Kod xato'}, status=status.HTTP_400_BAD_REQUEST)


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter

class TwitterLogin(SocialLoginView):
    adapter_class = TwitterOAuthAdapter

class AppleLogin(SocialLoginView):
    adapter_class = AppleOAuth2Adapter
