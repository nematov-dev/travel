from django.contrib import admin

from app_place.models import PlaceModel, PlaceCategoryModel, PlaceRatingModel,PlaceRatingImageModel

admin.site.register([PlaceModel, PlaceCategoryModel, PlaceRatingModel,PlaceRatingImageModel])
