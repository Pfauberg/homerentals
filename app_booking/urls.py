from django.urls import path
from . import views

urlpatterns = [
    path('bookings/',            views.BookingCreateView.as_view(),    name='api_booking_create'),
    path('bookings/my/',         views.MyBookingListView.as_view(),    name='api_my_bookings'),
    path('bookings/<int:pk>/',   views.BookingDetailView.as_view(),    name='api_booking_detail'),
    path('bookings/pending/',    views.PendingBookingListView.as_view(), name='api_pending_bookings'),
]
