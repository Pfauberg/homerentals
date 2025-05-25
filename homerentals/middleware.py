from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

class AdminLogoutRedirectMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path == '/admin/login/' and request.GET.get('next') == '/admin/':
            return redirect('/login/')
