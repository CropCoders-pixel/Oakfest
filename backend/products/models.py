from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name

class Product(models.Model):
    class ProductUnit(models.TextChoices):
        KG = 'kg', _('Kilogram')
        GRAM = 'g', _('Gram')
        PIECE = 'pc', _('Piece')
        DOZEN = 'dz', _('Dozen')
        LITER = 'l', _('Liter')
        
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    unit = models.CharField(
        max_length=2,
        choices=ProductUnit.choices,
        default=ProductUnit.KG
    )
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='product_images/')
    is_organic = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review for {self.product.name} by {self.user.email}"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']

class WasteReport(models.Model):
    class WasteType(models.TextChoices):
        ORGANIC = 'organic', _('Organic Waste')
        PACKAGING = 'packaging', _('Packaging Waste')
        OTHER = 'other', _('Other')
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    waste_type = models.CharField(
        max_length=10,
        choices=WasteType.choices,
        default=WasteType.ORGANIC
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='waste_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    points_awarded = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.email}'s waste report - {self.waste_type}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only calculate points for new reports
            points = int(self.quantity * 10)  # 10 points per unit
            if self.waste_type == self.WasteType.ORGANIC:
                points *= 2  # Double points for organic waste
            self.points_awarded = points
            # Update user's reward points
            self.user.reward_points += points
            self.user.save()
        super().save(*args, **kwargs)
