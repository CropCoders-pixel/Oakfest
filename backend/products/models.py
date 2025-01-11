from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images/', null=True)
    
    class Meta:
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name

class Product(models.Model):
    class ProductUnit(models.TextChoices):
        KG = 'kg', 'Kilogram'
        GRAM = 'g', 'Gram'
        PIECE = 'pc', 'Piece'
        DOZEN = 'dz', 'Dozen'
        LITER = 'l', 'Liter'
        
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=2, choices=ProductUnit.choices)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='product_images/')
    is_organic = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class WasteReport(models.Model):
    class WasteType(models.TextChoices):
        ORGANIC = 'organic', 'Organic Waste'
        PACKAGING = 'packaging', 'Packaging Waste'
        OTHER = 'other', 'Other'
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    waste_type = models.CharField(max_length=10, choices=WasteType.choices)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='waste_images/', null=True)
    points_awarded = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)