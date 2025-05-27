from rest_framework import serializers
from .models import Property
from django.utils import timezone

class PropertySerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source="owner.username")
    price_per_day = serializers.IntegerField(min_value=0)
    always_available = serializers.BooleanField(default=False)

    class Meta:
        model = Property
        fields = [
            "id", "title", "type", "description", "owner", "owner_username",
            "price_per_day", "city", "address", "beds", "status",
            "available_from", "available_to", "always_available",
            "created_at", "updated_at"
        ]
        read_only_fields = ("owner", "owner_username", "created_at", "updated_at")

    def validate(self, data):
        today = timezone.localdate()
        start = data.get("available_from", getattr(self.instance, "available_from", None))
        end = data.get("available_to", getattr(self.instance, "available_to", None))
        always = data.get("always_available", getattr(self.instance, "always_available", False))
        if start and start < today:
            raise serializers.ValidationError({"available_from": "Start date must be today or later."})
        if always:
            if end:
                raise serializers.ValidationError({"available_to": "Leave end date empty when always-available."})
        else:
            if not end:
                raise serializers.ValidationError({"available_to": "Provide end date or set always-available."})
            if end < start:
                raise serializers.ValidationError({"available_to": "End date must be ≥ start date."})
        return data
