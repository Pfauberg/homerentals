from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

class AdminLogoutRedirectMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path == '/admin/login/' and request.GET.get('next') == '/admin/':
            return redirect('/login/')


from django.utils import timezone
from app_property.models import Property

class AutoUpdateAvailabilityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        today = timezone.localdate()
        Property.objects.filter(
            always_available=False,
            available_to__lt=today,
            status="active"
        ).update(status="inactive")
        Property.objects.filter(
            status="active",
            available_from__lt=today
        ).update(available_from=today)
        return self.get_response(request)


from django.utils import timezone
from app_booking.models import Booking

class AutoUpdateBookingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        today = timezone.localdate()
        updated = Booking.objects.filter(
            status=Booking.Status.CONFIRMED,
            end_date__lt=today
        ).update(status=Booking.Status.FINISHED)
        Booking.objects.filter(
            status=Booking.Status.PENDING,
            created_at__lt=timezone.now() - timezone.timedelta(days=30)
        ).update(status=Booking.Status.DECLINED)
        return self.get_response(request)
