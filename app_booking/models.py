from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from app_accounts.models import CustomUser
from app_property.models import Property


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING    = 'pending',   'Pending'
        CONFIRMED  = 'confirmed', 'Confirmed'
        DECLINED   = 'declined',  'Declined'
        CANCELED   = 'canceled',  'Canceled'
        FINISHED   = 'finished',  'Finished'

    tenant       = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='bookings')
    property     = models.ForeignKey(
        Property,  on_delete=models.CASCADE, related_name='bookings')
    start_date   = models.DateField()
    end_date     = models.DateField()
    status       = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering        = ['-created_at']
        unique_together = [('property', 'start_date', 'end_date', 'status')]

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError({'end_date': 'End date must be ≥ start date.'})

        today = timezone.localdate()
        if self.start_date < today:
            raise ValidationError({'start_date': 'Start date must be in the future.'})

        if self.property.status != 'active':
            raise ValidationError('Property is not active.')

        if not self.property.always_available:
            if self.start_date < self.property.available_from:
                raise ValidationError('Booking starts before the property is available.')
            if self.property.available_to and self.end_date > self.property.available_to:
                raise ValidationError('Booking ends after the property is available.')

        if self.status in (self.Status.PENDING, self.Status.CONFIRMED):
            overlap = Booking.objects.filter(
                property=self.property,
                status=self.Status.CONFIRMED,
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
            ).exists()
            if overlap:
                raise ValidationError('Chosen dates overlap with another confirmed booking.')

    def save(self, *args, **kwargs):
        self.full_clean()
        is_new = self.pk is None

        prev_status = None
        if not is_new:
            old = Booking.objects.get(pk=self.pk)
            prev_status = old.status

        super().save(*args, **kwargs)

        if not is_new and self.status == self.Status.CONFIRMED and prev_status != self.Status.CONFIRMED:
            self._shift_property_window()

    @transaction.atomic
    def _shift_property_window(self):
        prop = Property.objects.select_for_update().get(pk=self.property_id)

        if prop.always_available:
            return

        if self.start_date <= prop.available_from <= self.end_date < prop.available_to:
            prop.available_from = self.end_date + timezone.timedelta(days=1)

        elif prop.available_from < self.start_date <= prop.available_to <= self.end_date:
            prop.available_to   = self.start_date - timezone.timedelta(days=1)

        elif self.start_date <= prop.available_from and self.end_date >= (prop.available_to or self.end_date):
            prop.status = 'inactive'

        prop.save(update_fields=['available_from', 'available_to', 'status'])
