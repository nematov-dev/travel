from modeltranslation.translator import register, TranslationOptions
from .models import PlaceModel, PlaceCategoryModel, PlaceRatingModel

@register(PlaceModel)
class PlaceTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(PlaceCategoryModel)
class PlaceCategoryTranslationOptions(TranslationOptions):
    fields = ('title',)