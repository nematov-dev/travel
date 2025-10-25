
from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenRefreshView,TokenBlacklistView
)

from app_user import views
from .views import GoogleLogin, FacebookLogin, TwitterLogin, AppleLogin

urlpatterns = [
    path('email/', views.EmailRegister.as_view(), name='email_register'),
    path('email/confirm/',views.EmailConfirm.as_view(),name="email_confirm"),
    path('register/user/',views.UserRegister.as_view(),name='register_user'),
    path('token/',views.LoginView.as_view(),name='token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/',TokenBlacklistView.as_view(),name='logout'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('reset/password/', views.ResetPassword.as_view(), name='reset_password'),
    path('reset/password/confirm/', views.ResetPasswordConfirm.as_view(), name='reset_password_confirm'),
    path('user/profile/',views.UserDetailView.as_view(),name='user_profile'),
    path('posts/create/',views.UserPost.as_view(),name="user_create_post"),
    path('posts/get',views.UserPostGet.as_view(),name="get_posts"),
    path('posts/public/all', views.AllPublicPostsList.as_view(), name='public-posts'),
    path('posts/<int:post_id>/like/', views.PostLikeToggle.as_view(), name='post-like'),
    path('user/<int:user_id>/detail/', views.UserDetailAPIView.as_view(), name='user-detail'),
    path('tags/', views.PostTagListCreateView.as_view(), name='tags-list'),
    path('tags/<int:tag_id>/posts/', views.TagPostListView.as_view(), name='tag-posts'),


    # # ✅ Social login endpointlar
    # path('google/', GoogleLogin.as_view(), name='google_login'),
    # path('facebook/', FacebookLogin.as_view(), name='facebook_login'),
    # path('twitter/', TwitterLogin.as_view(), name='twitter_login'),
    # path('apple/', AppleLogin.as_view(), name='apple_login'),
]