from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets, filters
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend


from app_place.models import PlaceModel, PlaceRatingModel
from .serializers import AdminUserSerializer


User = get_user_model()

class AdminDashboardStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = timezone.now().date()
        stats = {
            "total_users": User.objects.count(),
            "total_places": PlaceModel.objects.count(),
            "new_users_today": User.objects.filter(date_joined__date=today).count(),
        }
        return Response(stats)
    

class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_staff', 'is_active'] 
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'username']