from django.urls import path,include

from app_user import views

urlpatterns = [
    path('email/', views.EmailRegister.as_view(), name='email_register'),
    path('email/confirm/',views.EmailConfirm.as_view(),name="email_confirm"),
    path('register/user/',views.UserRegister.as_view(),name='register_user'),
    path('user/profile/',views.UserDetailView.as_view(),name='user_profile'),
    path('posts/create/',views.UserPost.as_view(),name="user_create_post"),
    path('post/<int:post_id>/delete/', views.UserPostDeleteView.as_view()),
    path('post/<int:post_id>/update/', views.UserPostUpdateView.as_view()),
    path('posts/get',views.UserPostGet.as_view(),name="get_posts"),
    path('posts/public/all', views.AllPublicPostsList.as_view(), name='public-posts'),
    path('posts/<int:post_id>/like/', views.PostLikeToggle.as_view(), name='post-like'),
    path('posts/<int:post_id>/comments/', views.PostCommentListView.as_view()),
    path('posts/<int:post_id>/comments/create/', views.PostCommentCreateView.as_view()),
    path('comments/<int:comment_id>/update/', views.PostCommentUpdateView.as_view()),
    path('comments/<int:comment_id>/delete/', views.PostCommentDeleteView.as_view()),
    path('user/<int:user_id>/detail/', views.UserDetailAPIView.as_view(), name='user-detail'),
    path('tags/', views.PostTagListCreateView.as_view(), name='tags-list'),
    path('tags/<int:tag_id>/posts/', views.TagPostListView.as_view(), name='tag-posts'),

]