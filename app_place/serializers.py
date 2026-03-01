from rest_framework import serializers
from django.db.models import Avg, Count


from .models import PlaceRatingModel, PlaceRatingImageModel,PlaceModel, PlaceCategoryModel



class PlaceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceCategoryModel
        fields = ['id', 'title']

class PlaceSerializer(serializers.ModelSerializer):
    category = PlaceCategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=PlaceCategoryModel.objects.all(),
        write_only=True,
        source='category'
    )

    ratings = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    ratings_count = serializers.SerializerMethodField()

    class Meta:
        model = PlaceModel
        fields = [
            'id',
            'avatar',
            'title',
            'website',
            'description',
            'latitude',
            'longitude',
            'category',
            'category_ids',
            'average_rating',
            'ratings_count',
            'ratings',
            'created_at',
        ]

    def get_ratings(self, obj):
        ratings = obj.ratings.all().select_related('user').prefetch_related('images')
        return PlaceRatingReadSerializer(ratings, many=True).data

    def get_average_rating(self, obj):
        return obj.ratings.aggregate(avg=Avg('value'))['avg'] or 0

    def get_ratings_count(self, obj):
        return obj.ratings.count()

class PlaceListSerializer(serializers.ModelSerializer):
    category = PlaceCategorySerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    ratings_count = serializers.SerializerMethodField()

    class Meta:
        model = PlaceModel
        fields = [
            'id', 'avatar', 'title', 'website', 
            'description', 'latitude', 'longitude', 
            'category', 'average_rating', 'ratings_count', 'created_at'
        ]

    def get_average_rating(self, obj):
        return obj.ratings.aggregate(avg=Avg('value'))['avg'] or 0

    def get_ratings_count(self, obj):
        return obj.ratings.count()


class PlaceRatingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceRatingImageModel
        fields = ['id', 'image']

class PlaceRatingReadSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    images = PlaceRatingImageSerializer(many=True, read_only=True)

    class Meta:
        model = PlaceRatingModel
        fields = ['id', 'user', 'place', 'value', 'description', 'images', 'created_at']


class PlaceRatingCreateSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = PlaceRatingModel
        fields = ['place', 'value', 'description'] 

    def create(self, validated_data):
        request = self.context.get('request')
        images = request.FILES.getlist('uploaded_images')
        
        rating = PlaceRatingModel.objects.create(
            user=request.user,
            **validated_data
        )
        
        for image in images:
            PlaceRatingImageModel.objects.create(rating=rating, image=image)
            
        return rating