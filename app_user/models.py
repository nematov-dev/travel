from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.db import models
from django.utils.text import slugify
import uuid

from app_common.models import BaseModel

#User Model


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email kiritish majburiy")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser uchun is_staff=True bo‘lishi kerak.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser uchun is_superuser=True bo‘lishi kerak.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=150, blank=True, null=True, unique=False)
    email = models.EmailField(unique=True)

    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    subscription = models.DateTimeField(auto_now_add=True)

    is_support = models.BooleanField(default=False)
    is_user = models.BooleanField(default=False)
    is_place = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # endi username majburiy emas

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    

#Post Tag Model 

class PostTag(BaseModel):
    title = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.title
    
    class Meta:
        verbose_name = 'Post Tag'
        verbose_name_plural = 'Post Tags'

# Post Media Model

class PostMedia(BaseModel):
    post = models.ForeignKey('UserPost',on_delete=models.CASCADE,related_name='medias')
    image = models.ImageField(upload_to='users/posts',blank=True,null=True)

    def __str__(self):
        return self.post.title if self.post else "No Post"

    class Meta:
        verbose_name = 'Post Media'
        verbose_name_plural = 'Post Medias'


# Post Like

class PostLike(BaseModel):
    post = models.ForeignKey('UserPost',on_delete=models.CASCADE,related_name='likes')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='likes')

    def __str__(self):
        return self.post.title if self.post else "No Post"

    class Meta:
        verbose_name = 'Post Like'
        verbose_name_plural = 'Post Likes'
        unique_together = ('post', 'user')

    
class UserPost(BaseModel):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="posts")
    tag = models.ForeignKey(PostTag,on_delete=models.CASCADE,related_name='posts',null=True,blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()

    location_name = models.CharField(max_length=255,blank=True,null=True)  # "Tashkent, Uzbekistan"
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    is_status = models.BooleanField(default=False) # post public or private

    def __str__(self) -> str:
        return self.title
    

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_suffix = str(uuid.uuid4())[:8]
            self.slug = f"{base_slug}-{unique_suffix}"
        super().save(*args, **kwargs)

    
    class Meta:
        verbose_name = 'User Post'
        verbose_name_plural = 'User Posts'



