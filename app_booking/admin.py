from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'tenant', 'property', 'start_date', 'end_date', 'status', 'created_at', 'updated_at'
    ]
    list_filter = ['status', 'property']
    search_fields = ['tenant__username', 'property__title']
