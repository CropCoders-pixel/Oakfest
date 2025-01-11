from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        ORDER = 'order', _('Order Update')
        PAYMENT = 'payment', _('Payment Update')
        DELIVERY = 'delivery', _('Delivery Update')
        REWARD = 'reward', _('Reward Points')
        SYSTEM = 'system', _('System Update')
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.type} notification for {self.user.email}"
    
    class Meta:
        ordering = ['-created_at']

class NotificationPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    order_updates = models.BooleanField(default=True)
    payment_updates = models.BooleanField(default=True)
    delivery_updates = models.BooleanField(default=True)
    reward_updates = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Notification preferences for {self.user.email}"

class NotificationChannel(models.Model):
    class ChannelType(models.TextChoices):
        EMAIL = 'email', _('Email')
        SMS = 'sms', _('SMS')
        PUSH = 'push', _('Push Notification')
        
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_channels'
    )
    channel = models.CharField(
        max_length=10,
        choices=ChannelType.choices
    )
    is_enabled = models.BooleanField(default=True)
    identifier = models.CharField(max_length=100)  # email address or phone number
    
    def __str__(self):
        return f"{self.channel} channel for {self.user.email}"
    
    class Meta:
        unique_together = ['user', 'channel']

class PushSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_subscriptions'
    )
    endpoint = models.URLField(max_length=500)
    p256dh = models.CharField(max_length=200)
    auth = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Push subscription for {self.user.email}"
    
    class Meta:
        unique_together = ['user', 'endpoint']
