from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from django.core.validators import RegexValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('farmer', 'Farmer'),
        ('consumer', 'Consumer'),
        ('admin', 'Admin')
    )

    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='consumer')
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)
    
    # Farmer specific fields
    farm_name = models.CharField(max_length=100, blank=True)
    farm_location = models.CharField(max_length=200, blank=True)
    farming_type = models.CharField(max_length=50, blank=True)
    
    # Reward points and contributions
    reward_points = models.IntegerField(default=0)
    total_waste_reports = models.IntegerField(default=0)
    total_waste_collected = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # Environmental impact metrics
    carbon_saved = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='CO2 emissions saved in kg'
    )
    trees_saved = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Equivalent number of trees saved'
    )
    water_saved = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Water saved in liters'
    )
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    # Firebase cloud messaging token
    fcm_token = models.TextField(blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
            models.Index(fields=['reward_points']),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def contribution_rank(self):
        """Get user's rank based on reward points"""
        return User.objects.filter(reward_points__gt=self.reward_points).count() + 1

    @property
    def contribution_percentile(self):
        """Get user's percentile among all users"""
        total_users = User.objects.count()
        if total_users > 0:
            return ((total_users - self.contribution_rank + 1) / total_users) * 100
        return 0

    def calculate_environmental_impact(self):
        """Calculate environmental impact based on waste reports"""
        # Impact factors (adjust these based on your research)
        IMPACT_FACTORS = {
            'cardboard': {'co2': 0.96, 'trees': 0.017, 'water': 3.8},
            'glass': {'co2': 0.28, 'trees': 0, 'water': 2.5},
            'metal': {'co2': 4.5, 'trees': 0, 'water': 8.0},
            'paper': {'co2': 0.96, 'trees': 0.017, 'water': 3.8},
            'plastic': {'co2': 1.5, 'trees': 0, 'water': 5.0},
            'trash': {'co2': 0.1, 'trees': 0, 'water': 0.5}
        }

        # Get all approved waste reports
        reports = self.waste_reports.filter(status='approved')
        
        # Reset impact metrics
        self.carbon_saved = 0
        self.trees_saved = 0
        self.water_saved = 0
        
        # Calculate impact
        for report in reports:
            factors = IMPACT_FACTORS.get(report.waste_type, {'co2': 0, 'trees': 0, 'water': 0})
            quantity = float(report.quantity)
            
            self.carbon_saved += quantity * factors['co2']
            self.trees_saved += quantity * factors['trees']
            self.water_saved += quantity * factors['water']
        
        self.save()
