from rest_framework import viewsets, permissions
from .permissions import IsOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator

from .models import PlaceModel, PlaceCategoryModel, PlaceRatingModel
from .serializers import PlaceSerializer, PlaceCategorySerializer, PlaceRatingCreateSerializer, PlaceRatingReadSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import PlaceFilter



class IsAdminUserOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class PlaceAdminViewSet(viewsets.ModelViewSet):
    queryset = PlaceModel.objects.all().prefetch_related(
        'category',
        'ratings__user',
        'ratings__images'
    )
    serializer_class = PlaceSerializer
    permission_classes = [IsAdminUserOnly]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering = ['-created_at']


class PlaceCategoryAdminViewSet(viewsets.ModelViewSet):
    queryset = PlaceCategoryModel.objects.all()
    serializer_class = PlaceCategorySerializer 
    permission_classes = [IsAdminUserOnly]


class PlacePublicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PlaceModel.objects.all().prefetch_related(
        'category',
        'ratings__user',
        'ratings__images'
    )
    serializer_class = PlaceSerializer
    permission_classes = [permissions.AllowAny]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_class = PlaceFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


@method_decorator(name='create', decorator=swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'uploaded_images', 
            openapi.IN_FORM, 
            type=openapi.TYPE_FILE, 
            description="Bir nechta rasm yuklash imkoniyati"
        ),
    ],
    responses={201: PlaceRatingReadSerializer()}
))
class PlaceRatingViewSet(viewsets.ModelViewSet):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    queryset = PlaceRatingModel.objects.all()
    serializer_class = PlaceRatingReadSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return PlaceRatingModel.objects.none()
        
        return PlaceRatingModel.objects.select_related('user', 'place').prefetch_related('images')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PlaceRatingCreateSerializer
        return PlaceRatingReadSerializer