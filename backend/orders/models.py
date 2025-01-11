from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        CONFIRMED = 'confirmed', _('Confirmed')
        PROCESSING = 'processing', _('Processing')
        SHIPPED = 'shipped', _('Shipped')
        DELIVERED = 'delivered', _('Delivered')
        CANCELLED = 'cancelled', _('Cancelled')
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    shipping_address = models.TextField()
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    points_used = models.IntegerField(default=0)
    points_earned = models.IntegerField(default=0)
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    
    def __str__(self):
        return f"Order #{self.id} by {self.user.email}"
    
    def calculate_points(self):
        # Calculate points earned (1 point per 10 rupees spent)
        self.points_earned = int(self.total_amount / 10)
        self.save()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
        ]

    def apply_points(self, points):
        if self.user.deduct_reward_points(points):
            # Convert points to rupees (1 point = 1 rupee)
            discount = points
            if discount <= self.total_amount:
                self.total_amount -= discount
                self.points_used = points
                self.save()
                return True
            self.user.add_reward_points(points)  # Refund points if can't apply
        return False

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only set price for new items
            self.price = self.product.price
        super().save(*args, **kwargs)

class Delivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    delivery_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='deliveries'
    )
    estimated_delivery = models.DateTimeField()
    actual_delivery = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('assigned', 'Assigned'),
            ('picked_up', 'Picked Up'),
            ('in_transit', 'In Transit'),
            ('delivered', 'Delivered'),
            ('failed', 'Failed')
        ],
        default='assigned'
    )
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Delivery for Order #{self.order.id}"
    
    class Meta:
        verbose_name_plural = 'deliveries'
