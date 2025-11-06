from rest_framework import serializers
from django.contrib.auth import get_user_model
from app_user import models

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

# User Post

class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PostMedia
        fields = ['id', 'image']

class PostTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PostTag
        fields = ['id', 'title']

class PostLikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = models.PostLike
        fields = ['id', 'user']

class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserPost
        fields = [
            'id', 'title', 'description', 'tag', 'location_name',
            'latitude', 'longitude', 'is_status'
        ]

    def create(self, validated_data):
        request = self.context['request']
        images = request.FILES.getlist('images')

        # 🔴 1. Kamida bitta rasm majburiy
        if not images:
            raise serializers.ValidationError({
                "images": "Kamida bitta rasm yuklashingiz kerak!"
            })

        # ✅ 2. Agar serializerda user bor bo‘lsa — olib tashlaymiz
        validated_data.pop('user', None)

        # ✅ 3. Postni yaratamiz
        post = models.UserPost.objects.create(user=request.user, **validated_data)

        # ✅ 4. Rasmlarni saqlaymiz
        for image in images:
            models.PostMedia.objects.create(post=post, image=image)

        return post
    
class UserPostDetailSerializer(serializers.ModelSerializer):
    """GET uchun to‘liq post malumoti"""
    medias = PostMediaSerializer(many=True, read_only=True)  # source kerak emas
    tag = PostTagSerializer(read_only=True)  # chunki tag OneToMany emas
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)  # yangi: faqat id

    class Meta:
        model = models.UserPost
        fields = [
            'id',
            'user_id',
            'title',
            'description',
            'location_name',
            'latitude',
            'longitude',
            'is_status',
            'tag',
            'medias',
            'likes_count',
        ]

class UserDetailSerializer(serializers.ModelSerializer):
    """Foydalanuvchi haqida batafsil ma’lumot va postlari bilan"""
    posts = UserPostDetailSerializer(many=True, read_only=True, source='user_posts')

    class Meta:
        model = models.User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'posts',
        ]

class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PostLike
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['user', 'created_at']

