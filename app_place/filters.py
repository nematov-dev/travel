import django_filters
from django.db.models import QuerySet
from math import radians, cos, sin, asin, sqrt

from .models import PlaceModel


class PlaceFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name='category__id')

    lat = django_filters.NumberFilter(method='filter_by_distance')
    lng = django_filters.NumberFilter(method='filter_by_distance')
    radius = django_filters.NumberFilter(method='filter_by_distance')

    class Meta:
        model = PlaceModel
        fields = ['category', 'lat', 'lng', 'radius']

    def filter_by_distance(self, queryset: QuerySet, name, value):
        lat = self.data.get('lat')
        lng = self.data.get('lng')
        radius = self.data.get('radius')

        if not (lat and lng and radius):
            return queryset

        lat = float(lat)
        lng = float(lng)
        radius = float(radius)

        result_ids = []

        for place in queryset:
            distance = self._distance(
                lat, lng,
                float(place.latitude),
                float(place.longitude)
            )
            if distance <= radius:
                result_ids.append(place.id)

        return queryset.filter(id__in=result_ids)

    def _distance(self, lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in km

        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)

        a = (
            sin(dlat / 2) ** 2 +
            cos(radians(lat1)) *
            cos(radians(lat2)) *
            sin(dlon / 2) ** 2
        )

        c = 2 * asin(sqrt(a))

        return R * c