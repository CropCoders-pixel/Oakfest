from rest_framework import serializers
from .models import Notification, NotificationPreference, PushSubscription

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            'id', 'type', 'title', 'message', 'link',
            'is_read', 'created_at'
        )
        read_only_fields = ('type', 'title', 'message', 'link', 'created_at')

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = (
            'order_updates', 'payment_updates', 'delivery_updates',
            'waste_reminders', 'reward_updates', 'marketing_emails'
        )

class PushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = ('endpoint', 'p256dh', 'auth')

    def create(self, validated_data):
        user = self.context['request'].user
        subscription, _ = PushSubscription.objects.update_or_create(
            user=user,
            endpoint=validated_data['endpoint'],
            defaults={
                'p256dh': validated_data['p256dh'],
                'auth': validated_data['auth']
            }
        )
        return subscription

class NotificationCountSerializer(serializers.Serializer):
    unread_count = serializers.IntegerField()
    order_updates = serializers.IntegerField()
    payment_updates = serializers.IntegerField()
    delivery_updates = serializers.IntegerField()
    waste_reminders = serializers.IntegerField()
    reward_updates = serializers.IntegerField()
    system_updates = serializers.IntegerField()
