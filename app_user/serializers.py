from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """Email allaqachon ro‘yxatdan o‘tmaganligini tekshirish"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email allaqachon ro‘yxatdan o‘tgan!")
        return value
    
class EmailConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.IntegerField()

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name','last_name','email','username','password','avatar','bio')
        
    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])  # 🔒 parolni hash qilish
        user.save()
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name','last_name','email','username','avatar','bio')
        extra_kwargs = {
            'email': {'read_only': True},  # Email o‘zgarmaydi
        }

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_new_password = serializers.CharField()

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()
    new_password = serializers.CharField()
    
