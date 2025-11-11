from django.urls import path
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
    # # ✅ Social login
    path('google/', views.GoogleLogin.as_view(), name='google_login'),
    path('facebook/', views.FacebookLogin.as_view(), name='facebook_login'),
    path('twitter/', views.TwitterLogin.as_view(), name='twitter_login'),
    path('apple/', views.AppleLogin.as_view(), name='apple_login'),
]