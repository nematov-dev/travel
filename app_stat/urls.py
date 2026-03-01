from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserAdminViewSet, AdminDashboardStatsView


router = DefaultRouter()
router.register(r'admin/users', UserAdminViewSet, basename='admin-users')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/dashboard/stats/', AdminDashboardStatsView.as_view(), name='admin-stats'),
]