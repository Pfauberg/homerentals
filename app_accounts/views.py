from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from .models import CustomUser
from rest_framework.views import APIView
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from .models import CustomUser
from .permissions import IsSuperUser
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, LoginSerializer, UserListSerializer



# HTML
def auth_portal(request):
    error = ""
    mode = 'login'
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/admin/')
        elif request.user.role == "landlord":
            return redirect('landlord_dashboard')
        else:
            return redirect('user_dashboard')

    if request.method == 'POST':
        if 'login' in request.POST:
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            user = authenticate(request, username=username, password=password)
            if user:
                django_login(request, user)
                if user.is_superuser:
                    return redirect('/admin/')
                elif user.role == "landlord":
                    return redirect('landlord_dashboard')
                else:
                    return redirect('user_dashboard')
            else:
                error = "Invalid username or password."
                mode = 'login'
        elif 'register' in request.POST:
            username = request.POST.get('username', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '').strip()
            password2 = request.POST.get('confirm_password', '').strip()
            role = request.POST.get('role', '').strip()
            mode = 'register'
            if password != password2:
                error = "Passwords do not match."
            elif not (username and first_name and last_name and email and password and role):
                error = "Fill out all fields."
            elif CustomUser.objects.filter(username=username).exists():
                error = "Username already exists."
            else:
                try:
                    user = CustomUser.objects.create_user(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password,
                        role=role,
                    )
                    django_login(request, user)
                    if user.role == "landlord":
                        return redirect('landlord_dashboard')
                    else:
                        return redirect('user_dashboard')
                except Exception as ex:
                    error = f"Registration error: {str(ex)}"

    return render(request, 'app_accounts/auth_portal.html', {'error': error, 'mode': mode})

def user_dashboard(request):
    return render(request, 'app_accounts/user_dashboard.html')

def landlord_dashboard(request):
    return render(request, 'app_accounts/landlord_dashboard.html')

def logout_view(request):
    django_logout(request)
    return redirect('auth_portal')



# API
class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"msg": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user_id": user.id,
                "role": user.role
            })
        return Response({'detail': 'Invalid credentials'}, status=400)
