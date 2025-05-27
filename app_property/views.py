# API
from rest_framework import generics, permissions
from .models import Property
from .serializers import PropertySerializer
from .permissions import IsLandlordOrAdminOrReadOnly

class PropertyListView(generics.ListAPIView):
    queryset = Property.objects.filter(status='active')
    serializer_class = PropertySerializer

class MyPropertyListCreateView(generics.ListCreateAPIView):
    serializer_class = PropertySerializer
    permission_classes = [IsLandlordOrAdminOrReadOnly]

    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class MyPropertyRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsLandlordOrAdminOrReadOnly]

class AdminPropertyListView(generics.ListAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAdminUser]

class AdminPropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAdminUser]



# HTML
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View, TemplateView, DetailView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Property
from django.views import View
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from difflib import SequenceMatcher

class UserSiteView(ListView):
    model = Property
    template_name = 'app_property/user_site.html'
    context_object_name = 'properties'
    queryset = Property.objects.filter(status='active').order_by('-created_at')

    def get_queryset(self):
        qs = super().get_queryset()
        sort = self.request.GET.get('sort', '')
        query = self.request.GET.get('q', '').strip()
        if query:
            res = []
            threshold = 0.7
            q_lower = query.lower()
            for prop in qs:
                title = prop.title.lower()
                desc = prop.description.lower()
                def best_match(text):
                    max_ratio = 0
                    for i in range(0, len(text) - len(q_lower) + 1):
                        chunk = text[i:i+len(q_lower)]
                        ratio = SequenceMatcher(None, q_lower, chunk).ratio()
                        max_ratio = max(max_ratio, ratio)
                    return max_ratio

                match_title = best_match(title)
                match_desc = best_match(desc)
                if match_title >= threshold or match_desc >= threshold:
                    res.append(prop)
            qs = res
        if sort == 'latest':
            if isinstance(qs, list):
                qs = sorted(qs, key=lambda x: (x.updated_at or x.created_at, x.created_at), reverse=True)
            else:
                qs = qs.order_by('-updated_at', '-created_at')
        elif sort == 'price_desc':
            if isinstance(qs, list):
                qs = sorted(qs, key=lambda x: x.price_per_day, reverse=True)
            else:
                qs = qs.order_by('-price_per_day')
        elif sort == 'price_asc':
            if isinstance(qs, list):
                qs = sorted(qs, key=lambda x: x.price_per_day)
            else:
                qs = qs.order_by('price_per_day')

        return qs

class UserPropertyDetailView(DetailView):
    model = Property
    template_name = 'app_property/user_property_detail.html'
    context_object_name = 'property'
    queryset = Property.objects.filter(status='active')


class LandlordSiteView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'app_property/landlord_site.html'

    def get(self, request):
        props = Property.objects.filter(owner=request.user).order_by('-created_at')
        today  = timezone.localdate().isoformat()
        return render(request, self.template_name,
                      {'properties': props, 'today': today})

    def post(self, request):
        if request.POST.get('action') == 'add':
            always = bool(request.POST.get('always_available'))
            try:
                Property.objects.create(
                    owner=request.user,
                    title=request.POST['title'],
                    type=request.POST['type'],
                    description=request.POST['description'],
                    price_per_day=int(request.POST['price_per_day']),
                    city=request.POST['city'],
                    address=request.POST['address'],
                    beds=request.POST['beds'],
                    available_from=request.POST['available_from'],
                    available_to=None if always else request.POST['available_to'],
                    always_available=always,
                    status='active'
                )
                messages.success(request, "Property added successfully.")
            except ValidationError as e:
                messages.error(request, "; ".join(sum(e.message_dict.values(), [])))
        return redirect('landlord_site')

    def test_func(self):
        return self.request.user.role == 'landlord' or self.request.user.is_superuser

class LandlordPropertyDetailView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'app_property/landlord_property_detail.html'

    def get_object(self):
        return get_object_or_404(Property, pk=self.kwargs['pk'], owner=self.request.user)

    def get(self, request, pk):
        prop = self.get_object()
        today = timezone.localdate().isoformat()
        return render(request, self.template_name, {'property': prop, 'today': today})

    def post(self, request, pk):
        prop = self.get_object()
        if request.POST.get('action') == 'delete':
            prop.delete()
            messages.success(request, "Property deleted successfully.")
            return redirect('landlord_site')
        prop.title = request.POST.get('title', prop.title)
        prop.type = request.POST.get('type', prop.type)
        prop.description = request.POST.get('description', prop.description)
        if 'price_per_day' in request.POST:
            prop.price_per_day = int(request.POST['price_per_day'])
        prop.city = request.POST.get('city', prop.city)
        prop.address = request.POST.get('address', prop.address)
        prop.beds = request.POST.get('beds', prop.beds)
        prop.status = request.POST.get('status', prop.status)
        prop.always_available = 'always_available' in request.POST
        prop.available_from = request.POST.get('available_from', prop.available_from)
        prop.available_to = None if prop.always_available else request.POST.get('available_to', prop.available_to)
        try:
            prop.save()
            messages.success(request, "Changes saved.")
        except ValidationError as e:
            messages.error(request, "; ".join(sum(e.message_dict.values(), [])))
        return redirect('landlord_site')

    def test_func(self):
        prop = Property.objects.filter(pk=self.kwargs['pk'], owner=self.request.user)
        return prop.exists() or self.request.user.is_superuser
