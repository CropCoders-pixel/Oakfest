from rest_framework import serializers
from django.db import models
from .models import Category, Product, Review, WasteReport
from users.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'user_email', 'user_name', 'product', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'user_email', 'user_name']

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    farmer_name = serializers.CharField(source='farmer.get_full_name', read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'unit', 'category', 'category_name', 
                 'farmer', 'farmer_name', 'is_organic', 'is_featured', 'image',
                 'average_rating', 'review_count']

class ProductSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    farmer_name = serializers.CharField(source='farmer.get_full_name', read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'unit', 'stock',
                 'category', 'category_name', 'farmer', 'farmer_name',
                 'is_organic', 'is_featured', 'image', 'created_at',
                 'updated_at', 'reviews', 'average_rating', 'review_count']
        read_only_fields = ['farmer', 'farmer_name', 'average_rating', 'review_count']
    
    def get_average_rating(self, obj):
        if hasattr(obj, 'average_rating'):
            return obj.average_rating
        return obj.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
    
    def get_review_count(self, obj):
        if hasattr(obj, 'review_count'):
            return obj.review_count
        return obj.reviews.count()

class WasteReportSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = WasteReport
        fields = ['id', 'user', 'user_email', 'user_name', 'waste_type', 
                 'quantity', 'description', 'image', 'created_at', 
                 'points_awarded']
        read_only_fields = ['user', 'user_email', 'user_name', 'points_awarded']

class WasteStatisticsSerializer(serializers.Serializer):
    total_waste = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_points = serializers.IntegerField()
    waste_by_type = serializers.DictField(
        child=serializers.DecimalField(max_digits=10, decimal_places=2)
    )
    monthly_stats = serializers.ListField(
        child=serializers.DictField(
            child=serializers.DecimalField(max_digits=10, decimal_places=2)
        )
    )
