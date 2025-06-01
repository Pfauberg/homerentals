from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Booking
from .serializers import (
    BookingCreateSerializer, BookingSerializer, BookingStatusUpdateSerializer
)
from .permissions import IsTenantOrLandlordOrAdmin, IsUserRole


class BookingCreateView(generics.CreateAPIView):
    serializer_class   = BookingCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsUserRole]


class MyBookingListView(generics.ListAPIView):
    serializer_class   = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'landlord':
            return Booking.objects.filter(property__owner=user)
        return Booking.objects.filter(tenant=user)


class BookingDetailView(generics.RetrieveUpdateAPIView):
    queryset          = Booking.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsTenantOrLandlordOrAdmin]

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return BookingStatusUpdateSerializer
        return BookingSerializer


class PendingBookingListView(generics.ListAPIView):
    serializer_class   = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role != 'landlord':
            return Booking.objects.none()
        return Booking.objects.filter(
            property__owner=user, status=Booking.Status.PENDING
        )
