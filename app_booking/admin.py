from django.contrib import admin
from .models import Booking, Review

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'tenant', 'property', 'start_date', 'end_date', 'status', 'created_at', 'updated_at'
    ]
    list_filter = ['status', 'property']
    search_fields = ['tenant__username', 'property__title']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'property', 'author', 'booking', 'rating', 'created_at']
    list_filter = ['property', 'rating']
    search_fields = ['property__title', 'author__username', 'text']
