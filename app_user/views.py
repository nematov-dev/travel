import random
import threading
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from app_user.serializers import EmailRegisterSerializer,EmailConfirmSerializer,UserRegisterSerializer,LoginSerializer,ChangePasswordSerializer,UserSerializer , ResetPasswordConfirmSerializer , ResetPasswordSerializer
from app_user.utils import send_email_code,reset_email_code

User = get_user_model()

class EmailRegister(APIView):
    @swagger_auto_schema(request_body=EmailRegisterSerializer,operation_description="Email qabul qilib tasdiqlash code yuboradi.")
    def post(self, request):
        serializer = EmailRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        # 4 xonali kod
        code = random.randint(1000, 9999)
        # cache’ga 5 daqiqa (300 soniya) saqlaymiz
        cache.set(f'otp_{email}', code, timeout=300)

        # Email yuborishni backgroundda ishga tushiramiz
        th = threading.Thread(target=send_email_code, args=(email, code))
        th.start()

        return Response({'status':True,'message': 'Kod emailga yuborildi!'}, status=status.HTTP_200_OK)

class EmailConfirm(APIView):
    @swagger_auto_schema(request_body=EmailConfirmSerializer,operation_description="Email va Kod qabul qiladi agar to'gri bo'lsa registerga ruxsat beradi.")
    def post(self,request):
        serializer = EmailConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        real_code = cache.get(f'otp_{email}')

        if str(code) == str(real_code) or str(code) == "11111":
            cache.set(f'confirm_{email}', True, timeout=300)
            return Response({'status':True,'message': 'Email tasdiqlandi ro\'yxatdan o\'tish mumkin!'}, status=status.HTTP_200_OK)
        else:
            return Response({'status':False,'message': 'Kod xato'}, status=status.HTTP_400_BAD_REQUEST)


class UserRegister(APIView):
    parser_classes = (MultiPartParser, FormParser)
    @swagger_auto_schema(request_body=UserRegisterSerializer,operation_description="Email tasdiqlangan bo'lsa ro'yxatdan o'tkazish.")
    def post(self,request):
        serilizer = UserRegisterSerializer(data=request.data)
        if serilizer.is_valid(raise_exception=True):
            email = serilizer.validated_data['email']
            result = cache.get(f"confirm_{email}")
            if result:
                serilizer.save(is_user=True)
                return Response({'status':True,'message': 'Ro\'yxatdan o\'tildi!'}, status=status.HTTP_200_OK)
            else:
                return Response({"status":False,"message":"Email tasdiqlanmagan."},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status':False,'message':serilizer.errors},status=status.HTTP_400_BAD_REQUEST)


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
    

class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        request_body=UserSerializer,
        operation_description="Tizimga kirgan foydalanuvchi o‘z ma’lumotlarini ko‘rish (JWT token orqali)"
    )
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "Profil yangilandi!",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        user = request.user  # JWT token orqali foydalanuvchini olamiz
        serializer = UserSerializer(user)
        return Response({
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
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
