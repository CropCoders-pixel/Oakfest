from rest_framework import serializers
from products.serializers import ProductSerializer
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.FloatField(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_id', 'quantity', 'total_price', 'created_at']
        read_only_fields = ['cart', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.FloatField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['user', 'total_price']
