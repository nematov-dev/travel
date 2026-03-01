from rest_framework.routers import DefaultRouter
from .views import PlaceAdminViewSet,PlaceCategoryAdminViewSet,PlacePublicViewSet,PlaceRatingViewSet,PlaceCategoryPublicViewSet

router = DefaultRouter()
router.register(r'admin/places', PlaceAdminViewSet, basename='admin-places')
router.register(r'admin/place-categories', PlaceCategoryAdminViewSet, basename='admin-place-categories')
router.register(r'places', PlacePublicViewSet, basename='places')
router.register(r'ratings', PlaceRatingViewSet, basename='ratings')
router.register(r'public-categories', PlaceCategoryPublicViewSet, basename='public-categories')


urlpatterns = router.urls