from rest_framework import generics, permissions, status
from rest_framework.response import Response

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView

from .models import Booking
from .serializers import (
    BookingCreateSerializer, BookingSerializer, BookingStatusUpdateSerializer
)
from .permissions import IsTenantOrLandlordOrAdmin, IsUserRole



# API
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



# HTML
class MyBookingsHTMLView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'app_booking/my_bookings.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        u = self.request.user
        if u.role == 'landlord':
            qs = Booking.objects.filter(property__owner=u).select_related('property', 'tenant')
        else:
            qs = Booking.objects.filter(tenant=u).select_related('property')
        return qs.order_by('-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_bookings = context['bookings']

        current = [
            b for b in all_bookings
            if b.status in ('pending', 'confirmed')
        ]
        history = [
            b for b in all_bookings
            if b.status in ('canceled', 'declined', 'finished')
        ]
        current.sort(key=lambda b: b.start_date)
        history.sort(key=lambda b: b.start_date, reverse=True)

        context['current_list'] = current
        context['history_list'] = history
        return context


class PendingBookingsHTMLView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Booking
    template_name = 'app_booking/pending_bookings.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.filter(property__owner=self.request.user).select_related('property', 'tenant')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_bookings = context['bookings']

        pending_list = [b for b in all_bookings if b.status == 'pending']
        current_list = [b for b in all_bookings if b.status == 'confirmed']
        history_list = [b for b in all_bookings if b.status in ('canceled', 'declined', 'finished')]

        pending_list.sort(key=lambda b: b.start_date)
        current_list.sort(key=lambda b: b.start_date)
        history_list.sort(key=lambda b: b.start_date, reverse=True)

        context['pending_list'] = pending_list
        context['current_list'] = current_list
        context['history_list'] = history_list
        return context

    def test_func(self):
        return self.request.user.role == 'landlord' or self.request.user.is_superuser
