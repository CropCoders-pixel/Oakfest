from rest_framework import serializers
from .models import Order, OrderItem, Delivery
from products.models import Product
from products.serializers import ProductSerializer
from users.serializers import UserSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Product.objects.all(),
        source='product'
    )
    
    class Meta:
        model = OrderItem
        fields = (
            'id', 'product', 'product_id', 'quantity',
            'price'
        )
        read_only_fields = ('price',)

class DeliverySerializer(serializers.ModelSerializer):
    delivery_person = UserSerializer(read_only=True)
    
    class Meta:
        model = Delivery
        fields = (
            'id', 'delivery_person', 'estimated_delivery',
            'actual_delivery', 'tracking_number', 'status',
            'notes'
        )
        read_only_fields = (
            'delivery_person', 'actual_delivery',
            'tracking_number', 'status'
        )

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = UserSerializer(read_only=True)
    delivery = DeliverySerializer(read_only=True)
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = (
            'id', 'user', 'status', 'total_amount',
            'shipping_address', 'phone', 'created_at',
            'updated_at', 'items', 'delivery', 'total_items',
            'points_used', 'points_earned', 'razorpay_order_id',
            'payment_status'
        )
        read_only_fields = (
            'user', 'total_amount', 'points_earned',
            'razorpay_order_id', 'payment_status'
        )
    
    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        validated_data['user'] = self.context['request'].user
        
        # Calculate total amount
        total_amount = sum(
            item['product'].price * item['quantity']
            for item in items_data
        )
        validated_data['total_amount'] = total_amount
        
        # Create order
        order = Order.objects.create(**validated_data)
        
        # Create order items
        for item_data in items_data:
            OrderItem.objects.create(
                order=order,
                product=item_data['product'],
                quantity=item_data['quantity'],
                price=item_data['product'].price
            )
        
        # Calculate and add points
        order.calculate_points()
        
        return order

class OrderListSerializer(serializers.ModelSerializer):
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = (
            'id', 'status', 'total_amount', 'created_at',
            'total_items', 'payment_status'
        )
    
    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status',)

class DeliveryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ('status', 'actual_delivery', 'notes')

class ApplyPointsSerializer(serializers.Serializer):
    points = serializers.IntegerField(min_value=1)

class PaymentVerificationSerializer(serializers.Serializer):
    razorpay_payment_id = serializers.CharField()
    razorpay_order_id = serializers.CharField()
    razorpay_signature = serializers.CharField()
