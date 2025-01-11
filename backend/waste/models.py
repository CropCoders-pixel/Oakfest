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
        CARDBOARD = 'cardboard', _('Cardboard')
        GLASS = 'glass', _('Glass')
        METAL = 'metal', _('Metal')
        PAPER = 'paper', _('Paper')
        PLASTIC = 'plastic', _('Plastic')
        TRASH = 'trash', _('Trash')
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='waste_reports'
    )
    category = models.ForeignKey(WasteCategory, on_delete=models.CASCADE)
    waste_type = models.CharField(
        max_length=10,
        choices=WasteType.choices,
        help_text=_('Type of waste material')
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='waste_images/',
        help_text=_('Image must clearly show the waste type')
    )
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
        return f"{self.user.email}'s {self.get_waste_type_display()} waste report"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only calculate points for new reports
            # Base points based on waste type
            points_map = {
                'cardboard': 10,
                'glass': 15,
                'metal': 20,
                'paper': 10,
                'plastic': 15,
                'trash': 5
            }
            self.points_awarded = points_map.get(self.waste_type, 0)
            
            # Update user's reward points if report is approved
            if self.status == 'approved':
                self.user.reward_points += self.points_awarded
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
