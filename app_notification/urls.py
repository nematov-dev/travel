from django.urls import path
from app_notification import views


urlpatterns = [
    path(
        '',
        views.NotificationListView.as_view(),
        name='notification-list'
    ),

    path(
        'unread-count/',
        views.NotificationUnreadCount.as_view(),
        name='notification-unread-count'
    ),

    path(
        '<int:pk>/mark-as-read/',
        views.NotificationMarkAsRead.as_view(),
        name='notification-mark-as-read'
    ),

    path(
    'mark-all-as-read/',
    views.NotificationMarkAllAsRead.as_view(),
    name='notification-mark-all-as-read'
),
]