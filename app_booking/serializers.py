from rest_framework import serializers
from django.db import transaction
from .models import Booking, Review
from django.core.exceptions import ValidationError as DjangoValidationError



class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Booking
        fields = ['id', 'property', 'start_date', 'end_date', 'status']
        read_only_fields = ['id', 'status']

    def validate(self, attrs):
        attrs['tenant'] = self.context['request'].user
        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated):
        validated['tenant'] = self.context['request'].user
        validated['status'] = Booking.Status.PENDING
        try:
            return super().create(validated)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict or e.messages)


class BookingSerializer(serializers.ModelSerializer):
    tenant_username   = serializers.ReadOnlyField(source='tenant.username')
    property_title    = serializers.ReadOnlyField(source='property.title')
    property_id       = serializers.ReadOnlyField(source='property.id')

    class Meta:
        model  = Booking
        fields = [
            'id', 'tenant', 'tenant_username', 'property',
            'property_title', 'property_id',
            'start_date', 'end_date', 'status',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields


class BookingStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Booking
        fields = ['status']

    def validate(self, attrs):
        new_status = attrs['status']
        request = self.context['request']
        booking = self.instance
        user = request.user

        if booking.status in [Booking.Status.CONFIRMED, Booking.Status.DECLINED]:
            raise serializers.ValidationError('You cannot change status after it is confirmed or declined.')

        if user.role == 'landlord':
            allowed = [Booking.Status.CONFIRMED, Booking.Status.DECLINED]
        else:
            allowed = [Booking.Status.CANCELED]

        if new_status not in allowed:
            raise serializers.ValidationError('You cannot set this status.')
        return attrs

    def update(self, instance, validated_data):
        prev = instance.status
        instance.status = validated_data['status']
        try:
            instance.save()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict or e.messages)
        return instance


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'property', 'booking', 'rating', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        user = self.context['request'].user
        booking = attrs.get('booking')
        prop = attrs.get('property')
        if booking.tenant != user:
            raise serializers.ValidationError("You can only review bookings you made.")
        if booking.property != prop:
            raise serializers.ValidationError("Booking does not match property.")
        if booking.status != 'finished':
            raise serializers.ValidationError("Can only review after booking is finished.")
        if Review.objects.filter(property=prop, author=user, booking=booking).exists():
            raise serializers.ValidationError("You have already reviewed this booking.")
        rating = attrs.get('rating')
        if not (1 <= rating <= 5):
            raise serializers.ValidationError("Rating must be 1-5.")
        return attrs

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ReviewListSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    class Meta:
        model = Review
        fields = ['id', 'property', 'author', 'author_username', 'booking', 'rating', 'text', 'created_at']
        read_only_fields = fields


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'text']

    def validate(self, attrs):
        rating = attrs.get('rating', getattr(self.instance, 'rating', None))
        if not (1 <= rating <= 5):
            raise serializers.ValidationError("Rating must be 1-5.")
        return attrs
