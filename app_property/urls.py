from django.urls import path
from . import views
from .views import UserSiteView, LandlordSiteView, UserPropertyDetailView, LandlordPropertyDetailView

urlpatterns = [
    path('public/', views.PropertyListView.as_view(), name='public_property_list'),
    path('my/', views.MyPropertyListCreateView.as_view(), name='my_property_list_create'),
    path('my/<int:pk>/', views.MyPropertyRetrieveUpdateDestroyView.as_view(), name='my_property_detail'),
    path('admin-all/', views.AdminPropertyListView.as_view(), name='admin_property_list'),
    path('admin/<int:pk>/', views.AdminPropertyDetailView.as_view(), name='admin_property_detail'),
    path('user/', UserSiteView.as_view(), name='user_site'),
    path('user/<int:pk>/', UserPropertyDetailView.as_view(), name='user_property_detail'),
    path('landlord/', LandlordSiteView.as_view(), name='landlord_site'),
    path('landlord/<int:pk>/', LandlordPropertyDetailView.as_view(), name='landlord_property_detail'),
]
