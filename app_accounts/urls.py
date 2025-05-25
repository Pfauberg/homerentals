from django.urls import path
from . import views

urlpatterns = [
    path('', views.auth_portal, name='auth_portal'),
    path('login/', views.auth_portal, name='login'),
    path('user/', views.user_dashboard, name='user_dashboard'),
    path('landlord/', views.landlord_dashboard, name='landlord_dashboard'),
    path('logout/', views.logout_view, name='logout'),
]
