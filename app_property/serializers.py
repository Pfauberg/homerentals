from rest_framework import serializers
from .models import Property

class PropertySerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source="owner.username")
    price_per_day = serializers.IntegerField(min_value=0)
    class Meta:
        model = Property
        fields = [
            "id", "title", "type", "description", "owner", "owner_username",
            "price_per_day", "city", "address", "beds", "status",
            "available_from", "available_to", "created_at", "updated_at"
        ]
        read_only_fields = ("owner", "owner_username", "created_at", "updated_at")
