from rest_framework import serializers
from .models import Property
from django.utils import timezone

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

    def validate(self, data):
        today = timezone.localdate()
        start = data.get("available_from", getattr(self.instance, "available_from", None))
        end = data.get("available_to", getattr(self.instance, "available_to", None))
        if start and start < today:
            raise serializers.ValidationError({"available_from": "Start date must be today or later."})
        if start and end and end < start:
            raise serializers.ValidationError({"available_to": "End date must be the same day or after start date."})
        return data
