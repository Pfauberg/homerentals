from django.contrib.auth.backends import ModelBackend
from app_accounts.models import CustomUser

class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None
        if username is None:
            username = kwargs.get('username')
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(email=username)
            except CustomUser.DoesNotExist:
                return None
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
