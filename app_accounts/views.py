from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from .models import CustomUser

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
