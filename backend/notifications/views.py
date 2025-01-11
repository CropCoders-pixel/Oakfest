from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Notification, NotificationPreference, PushSubscription
from .serializers import (
    NotificationSerializer,
    NotificationPreferenceSerializer,
    PushSubscriptionSerializer,
    NotificationCountSerializer
)
from .utils import send_push_notification

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'is_read']
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'message': 'All notifications marked as read'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        counts = {
            'unread_count': self.get_queryset().filter(is_read=False).count(),
            'order_updates': self.get_queryset().filter(type='order', is_read=False).count(),
            'payment_updates': self.get_queryset().filter(type='payment', is_read=False).count(),
            'delivery_updates': self.get_queryset().filter(type='delivery', is_read=False).count(),
            'waste_reminders': self.get_queryset().filter(type='waste', is_read=False).count(),
            'reward_updates': self.get_queryset().filter(type='reward', is_read=False).count(),
            'system_updates': self.get_queryset().filter(type='system', is_read=False).count(),
        }
        serializer = NotificationCountSerializer(data=counts)
        serializer.is_valid()
        return Response(serializer.data)

class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_object(self):
        return self.get_queryset().first()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            # Create if doesn't exist
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data)
        
        # Update existing
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class PushSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = PushSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PushSubscription.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        subscription = serializer.save(user=self.request.user)
        # Send a test notification
        send_push_notification(
            subscription,
            'Welcome!',
            'You have successfully subscribed to push notifications.'
        )
    
    @action(detail=False, methods=['delete'])
    def unsubscribe(self, request):
        endpoint = request.data.get('endpoint')
        if endpoint:
            PushSubscription.objects.filter(
                user=request.user,
                endpoint=endpoint
            ).delete()
            return Response({'message': 'Successfully unsubscribed'})
        return Response({
            'error': 'Endpoint is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def test(self, request):
        subscriptions = self.get_queryset()
        for subscription in subscriptions:
            send_push_notification(
                subscription,
                'Test Notification',
                'This is a test notification.'
            )
        return Response({'message': 'Test notifications sent'})
