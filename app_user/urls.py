from django.urls import path
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,TokenBlacklistView
)

from app_user import views

urlpatterns = [
    path('email/', views.EmailRegister.as_view(), name='email_register'),
    path('email/confirm/',views.EmailConfirm.as_view(),name="email_confirm"),
    path('register/user/',views.UserRegister.as_view(),name='register_user'),
    path('token/',views.LoginView.as_view(),name='token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/',TokenBlacklistView.as_view(),name='logout'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('user/profile/',views.UserDetailView.as_view(),name='user_profile')
]