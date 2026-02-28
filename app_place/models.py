from django.db import models
from django.contrib.auth import get_user_model

from app_common.models import BaseModel

User = get_user_model()

class PlaceModel(BaseModel):
    avatar = models.ImageField(upload_to='place/avatar',null=True,blank=True)
    category = models.ManyToManyField('PlaceCategoryModel',related_name='places')
    title = models.CharField(max_length=255)
    website = models.CharField(max_length=128)
    description = models.TextField(blank=True,null=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self) -> str:
        return self.title
    
    class Meta:
        verbose_name = 'Place'
        verbose_name_plural = 'Places'

class PlaceCategoryModel(BaseModel):
    title = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.title
    
    class Meta:
        verbose_name = 'Place_category'
        verbose_name_plural = 'Place_categories'
    
class PlaceRatingModel(BaseModel):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='ratings')
    place = models.ForeignKey(PlaceModel,on_delete=models.CASCADE,related_name='ratings')
    value = models.PositiveIntegerField(default=1)
    description = models.TextField(null=True,blank=True)

    def __str__(self) -> str:
        return f"{self.user.username} rating for {self.place.title}"
    
    class Meta:
        verbose_name = 'Place_rating'
        verbose_name_plural = 'Place_ratings'
        unique_together = ('user', 'place')


class PlaceRatingImageModel(BaseModel):
    rating = models.ForeignKey(PlaceRatingModel,on_delete=models.CASCADE,related_name='images')
    image = models.ImageField(upload_to='place/rating/image')

    def __str__(self) -> str:
        return f"{self.rating.place.title} image"
    
    class Meta:
        verbose_name = 'Place_image'
        verbose_name_plural = 'Place_images'


