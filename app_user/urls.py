
from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenRefreshView,TokenBlacklistView
)

from app_user import views

urlpatterns = [
    path('email/', views.EmailRegister.as_view(), name='email_register'),
    path('email/confirm/',views.EmailConfirm.as_view(),name="email_confirm"),
    path('register/user/',views.UserRegister.as_view(),name='register_user'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/',TokenBlacklistView.as_view(),name='logout'),
    path('user/profile/',views.UserDetailView.as_view(),name='user_profile'),
    path('posts/create/',views.UserPost.as_view(),name="user_create_post"),
    path('posts/get',views.UserPostGet.as_view(),name="get_posts"),
    path('posts/public/all', views.AllPublicPostsList.as_view(), name='public-posts'),
    path('posts/<int:post_id>/like/', views.PostLikeToggle.as_view(), name='post-like'),
    path('user/<int:user_id>/detail/', views.UserDetailAPIView.as_view(), name='user-detail'),
    path('tags/', views.PostTagListCreateView.as_view(), name='tags-list'),
    path('tags/<int:tag_id>/posts/', views.TagPostListView.as_view(), name='tag-posts'),

]