from django.contrib import admin
from .models import Property

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'type', 'owner', 'status', 'city', 'address',
        'price_per_day', 'beds', 'available_from', 'available_to', 'created_at'
    ]
    list_filter = ['type', 'status', 'city', 'owner']
    search_fields = ['title', 'city', 'address', 'owner__username']
