from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenRefreshView,TokenBlacklistView
)


from app_auth import views

urlpatterns = [
    path('token/',views.LoginView.as_view(),name='token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/',TokenBlacklistView.as_view(),name='logout'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('reset/password/', views.ResetPassword.as_view(), name='reset_password'),
    path('reset/password/confirm/', views.ResetPasswordConfirm.as_view(), name='reset_password_confirm'),
]