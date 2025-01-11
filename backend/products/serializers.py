from rest_framework import serializers
from django.db.models import Avg
from users.serializers import UserSerializer
from .models import Product, ProductReview

class ProductSerializer(serializers.ModelSerializer):
    farmer = UserSerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock', 
            'unit', 'category', 'image', 'farmer',
            'average_rating', 'review_count', 'created_at'
        ]
        read_only_fields = ['farmer', 'average_rating', 'review_count']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        reviews = instance.reviews.all()
        representation['average_rating'] = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        representation['review_count'] = reviews.count()
        return representation

class ProductReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'user', 'product', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'product']
