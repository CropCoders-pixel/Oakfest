from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name

class Product(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('l', 'Litre'),
        ('pc', 'Piece'),
        ('g', 'Gram'),
        ('ml', 'Millilitre'),
    ]
    
    CATEGORY_CHOICES = [
        ('fruits', 'Fruits'),
        ('vegetables', 'Vegetables'),
        ('dairy', 'Dairy Products'),
        ('grains', 'Grains'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=2, choices=UNIT_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} by {self.farmer.username}"
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category']),
            models.Index(fields=['farmer']),
            models.Index(fields=['is_active']),
        ]

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"
