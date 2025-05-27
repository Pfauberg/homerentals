from django.db import models
from app_accounts.models import CustomUser
from django.utils import timezone
from django.core.exceptions import ValidationError

class Property(models.Model):
    TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('studio', 'Studio'),
        ('villa', 'Villa'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    title = models.CharField('Title', max_length=255)
    type = models.CharField('Type', max_length=16, choices=TYPE_CHOICES)
    description = models.TextField('Description')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='properties', verbose_name='Landlord')
    price_per_day = models.PositiveIntegerField('Price per 24 hours (€)')
    city = models.CharField('City', max_length=127)
    address = models.CharField('Address', max_length=255)
    beds = models.PositiveIntegerField('Number of beds')
    status = models.CharField('Active status', max_length=8, choices=STATUS_CHOICES, default='active')
    available_from = models.DateField('Available from')
    available_to = models.DateField('Available to', null=True, blank=True)
    always_available = models.BooleanField('Always available', default=False)
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.city}) [{self.get_type_display()}]"

    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"
        ordering = ['-created_at']

    def clean(self):
        today = timezone.localdate()
        if self.available_from < today:
            raise ValidationError({"available_from": "Start date can’t be earlier than today."})
        if self.always_available:
            if self.available_to:
                raise ValidationError({"available_to": "End date must be empty when always-available flag is set."})
        else:
            if not self.available_to:
                raise ValidationError({"available_to": "Specify end date or tick “Always available”."})
            if self.available_to < self.available_from:
                raise ValidationError({"available_to": "End date can’t be earlier than start date."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
