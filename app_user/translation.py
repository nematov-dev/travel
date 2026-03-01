from modeltranslation.translator import register, TranslationOptions
from .models import PostTag, UserPost

@register(PostTag)
class PostTagTranslationOptions(TranslationOptions):
    fields = ('title',)