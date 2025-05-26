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
        today = timezone.now().date()
        Property.objects.filter(available_to__lt=today).update(available_to=today)
        Property.objects.filter(available_from__lt=today).update(available_from=today)
        return self.get_response(request)
