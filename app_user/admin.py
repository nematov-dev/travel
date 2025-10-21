from django.contrib import admin

from app_user.models import UserPost,PostLike,PostMedia,PostTag

from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'is_active', 'is_staff', 'is_support', 'is_user', 'is_place')
    list_filter = ('is_support', 'is_user', 'is_place', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'avatar', 'bio')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_support', 'is_user', 'is_place')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register([UserPost,PostLike,PostMedia,PostTag])
