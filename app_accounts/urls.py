from django.urls import path
from . import views
from .views import RegisterAPIView, LoginAPIView, UserListView, UserDetailView

urlpatterns = [
    path('', views.auth_portal, name='auth_portal'),
    path('login/', views.auth_portal, name='login'),
    path('user/', views.user_dashboard, name='user_dashboard'),
    path('landlord/', views.landlord_dashboard, name='landlord_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('api/register/', RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', LoginAPIView.as_view(), name='api_login'),
    path('api/users/', UserListView.as_view(), name='api_users'),
    path('api/users/<int:pk>/', UserDetailView.as_view(), name='api_user_detail'),
]
