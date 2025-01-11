from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

class WasteCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    points_per_unit = models.IntegerField(default=10)
    
    class Meta:
        verbose_name_plural = 'Waste Categories'
    
    def __str__(self):
        return self.name

class WasteReport(models.Model):
    class WasteType(models.TextChoices):
        ORGANIC = 'organic', _('Organic Waste')
        PACKAGING = 'packaging', _('Packaging Waste')
        FOOD = 'food', _('Food Waste')
        OTHER = 'other', _('Other')
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='waste_reports'
    )
    category = models.ForeignKey(WasteCategory, on_delete=models.CASCADE)
    waste_type = models.CharField(max_length=10, choices=WasteType.choices)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='waste_images/', null=True, blank=True)
    points_awarded = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('collected', 'Collected')
        ],
        default='pending'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email}'s {self.waste_type} waste report"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only calculate points for new reports
            points = int(self.quantity * self.category.points_per_unit)
            if self.waste_type == self.WasteType.ORGANIC:
                points *= 2  # Double points for organic waste
            self.points_awarded = points
            
            # Update user's reward points if report is approved
            if self.status == 'approved':
                self.user.reward_points += points
                self.user.save()
        super().save(*args, **kwargs)

class WasteCollection(models.Model):
    waste_report = models.OneToOneField(WasteReport, on_delete=models.CASCADE)
    collector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='waste_collections'
    )
    collection_date = models.DateTimeField()
    collected_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-collection_date']
    
    def __str__(self):
        return f"Collection for {self.waste_report}"
