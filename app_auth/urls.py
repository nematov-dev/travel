from django.urls import path

from app_auth import views

urlpatterns = [
    path('token/',views.LoginView.as_view(),name='token'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('reset/password/', views.ResetPassword.as_view(), name='reset_password'),
    path('reset/password/confirm/', views.ResetPasswordConfirm.as_view(), name='reset_password_confirm'),
    # # ✅ Social login endpointlar
    path('google/', views.GoogleLogin.as_view(), name='google_login'),
    path('facebook/', views.FacebookLogin.as_view(), name='facebook_login'),
    path('twitter/', views.TwitterLogin.as_view(), name='twitter_login'),
    path('apple/', views.AppleLogin.as_view(), name='apple_login'),
]