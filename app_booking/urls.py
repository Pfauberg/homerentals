from django.urls import path
from . import views

urlpatterns = [
    path('bookings/',            views.BookingCreateView.as_view(),    name='api_booking_create'),
    path('bookings/my/',         views.MyBookingListView.as_view(),    name='api_my_bookings'),
    path('bookings/<int:pk>/',   views.BookingDetailView.as_view(),    name='api_booking_detail'),
    path('bookings/pending/',    views.PendingBookingListView.as_view(), name='api_pending_bookings'),
    path('bookings/my-html/',       views.MyBookingsHTMLView.as_view(),       name='my_bookings_html'),
    path('bookings/pending-html/',  views.PendingBookingsHTMLView.as_view(),  name='pending_bookings_html'),
]
