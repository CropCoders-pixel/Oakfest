from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
import razorpay
from .models import Order, OrderItem, Delivery
from .serializers import (
    OrderSerializer,
    OrderListSerializer,
    OrderStatusUpdateSerializer,
    DeliverySerializer,
    DeliveryUpdateSerializer,
    ApplyPointsSerializer,
    PaymentVerificationSerializer
)
from users.permissions import IsConsumer
from notifications.utils import send_notification

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'payment_status']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        elif user.user_type == 'farmer':
            return Order.objects.filter(items__product__farmer=user).distinct()
        return Order.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'update_status':
            return OrderStatusUpdateSerializer
        elif self.action == 'apply_points':
            return ApplyPointsSerializer
        elif self.action == 'verify_payment':
            return PaymentVerificationSerializer
        return OrderSerializer
    
    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        # Create Razorpay order
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        razorpay_order = client.order.create({
            'amount': int(order.total_amount * 100),  # Amount in paise
            'currency': 'INR',
            'payment_capture': 1
        })
        order.razorpay_order_id = razorpay_order['id']
        order.save()
        
        # Send notification
        send_notification(
            user=order.user,
            type='order',
            title='Order Created',
            message=f'Your order #{order.id} has been created successfully.'
        )
    
    @action(detail=True, methods=['post'])
    def apply_points(self, request, pk=None):
        order = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            points = serializer.validated_data['points']
            if order.apply_points(points):
                return Response({
                    'message': 'Points applied successfully',
                    'new_total': order.total_amount
                })
            return Response({
                'error': 'Could not apply points'
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def verify_payment(self, request, pk=None):
        order = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            
            # Verify signature
            try:
                client.utility.verify_payment_signature({
                    'razorpay_order_id': order.razorpay_order_id,
                    'razorpay_payment_id': serializer.validated_data['razorpay_payment_id'],
                    'razorpay_signature': serializer.validated_data['razorpay_signature']
                })
                
                # Update order
                order.payment_status = 'completed'
                order.status = 'confirmed'
                order.razorpay_payment_id = serializer.validated_data['razorpay_payment_id']
                order.save()
                
                # Calculate and add points
                order.calculate_points()
                
                # Send notification
                send_notification(
                    user=order.user,
                    type='payment',
                    title='Payment Successful',
                    message=f'Payment for order #{order.id} has been received.'
                )
                
                return Response({'message': 'Payment verified successfully'})
            except Exception as e:
                return Response({
                    'error': 'Payment verification failed'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            order.status = serializer.validated_data['status']
            order.save()
            
            # Send notification
            send_notification(
                user=order.user,
                type='order',
                title='Order Status Updated',
                message=f'Your order #{order.id} status has been updated to {order.status}.'
            )
            
            return Response({'message': 'Order status updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        user = request.user
        if user.user_type == 'farmer':
            orders = Order.objects.filter(items__product__farmer=user)
        else:
            orders = Order.objects.filter(user=user)
        
        total_orders = orders.count()
        completed_orders = orders.filter(status='delivered').count()
        total_revenue = sum(order.total_amount for order in orders)
        
        return Response({
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'total_revenue': total_revenue,
            'completion_rate': (completed_orders / total_orders * 100) if total_orders > 0 else 0
        })

class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Delivery.objects.all()
        elif user.user_type == 'farmer':
            return Delivery.objects.filter(order__items__product__farmer=user)
        return Delivery.objects.filter(order__user=user)
    
    def get_serializer_class(self):
        if self.action == 'update_status':
            return DeliveryUpdateSerializer
        return DeliverySerializer
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        delivery = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            delivery.status = serializer.validated_data['status']
            if delivery.status == 'delivered':
                delivery.actual_delivery = serializer.validated_data.get('actual_delivery')
            delivery.notes = serializer.validated_data.get('notes', '')
            delivery.save()
            
            # Update order status
            order = delivery.order
            if delivery.status == 'delivered':
                order.status = 'delivered'
            elif delivery.status == 'failed':
                order.status = 'cancelled'
            order.save()
            
            # Send notification
            send_notification(
                user=order.user,
                type='delivery',
                title='Delivery Status Updated',
                message=f'Delivery status for order #{order.id} has been updated to {delivery.status}.'
            )
            
            return Response({'message': 'Delivery status updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
