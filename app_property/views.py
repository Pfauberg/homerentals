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
from django.views.generic import ListView, View, DetailView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from difflib import SequenceMatcher
from django.db.models import Q, Min, Max

class UserSiteView(ListView):
    model = Property
    template_name = 'app_property/user_site.html'
    context_object_name = 'properties'

    def get_queryset(self):
        qs = Property.objects.filter(status='active')

        g = self.request.GET

        p_min = g.get('price_min')
        p_max = g.get('price_max')
        if p_min:
            qs = qs.filter(price_per_day__gte=int(p_min))
        if p_max:
            qs = qs.filter(price_per_day__lte=int(p_max))

        cities = g.getlist('city')
        if cities:
            qs = qs.filter(city__in=cities)

        types = g.getlist('type')
        if types:
            qs = qs.filter(type__in=types)

        b_min = g.get('beds_min')
        b_max = g.get('beds_max')
        if b_min:
            qs = qs.filter(beds__gte=int(b_min))
        if b_max:
            qs = qs.filter(beds__lte=int(b_max))

        a_only = g.get('always_only')
        a_from = g.get('avail_start')
        a_to   = g.get('avail_end')
        if a_only:
            qs = qs.filter(always_available=True)
        elif a_from and a_to:
            qs = qs.filter(
                Q(always_available=True) |
                (Q(available_from__lte=a_from) &
                 (Q(available_to__isnull=True) | Q(available_to__gte=a_to)))
            )

        posted = g.get('posted')
        if posted in ('day', 'week', 'month'):
            now = timezone.now()
            delta = {'day': 1, 'week': 7, 'month': 30}[posted]
            qs = qs.filter(created_at__gte=now - timedelta(days=delta))

        query = g.get('q', '').strip()
        if query:
            res, thresh, ql = [], 0.7, query.lower()

            def best_match(txt):
                best = 0
                for i in range(0, len(txt) - len(ql) + 1):
                    best = max(best, SequenceMatcher(None, ql, txt[i:i+len(ql)]).ratio())
                return best

            for pr in qs:
                if best_match(pr.title.lower()) >= thresh or best_match(pr.description.lower()) >= thresh:
                    res.append(pr)
            qs = res

        sort = g.get('sort', '')
        if sort == 'latest':
            key = lambda x: (x.updated_at or x.created_at, x.created_at)
            qs = sorted(qs, key=key, reverse=True) if isinstance(qs, list) else qs.order_by('-updated_at', '-created_at')
        elif sort == 'price_desc':
            qs = sorted(qs, key=lambda x: x.price_per_day, reverse=True) if isinstance(qs, list) else qs.order_by('-price_per_day')
        elif sort == 'price_asc':
            qs = sorted(qs, key=lambda x: x.price_per_day) if isinstance(qs, list) else qs.order_by('price_per_day')

        self._result_count = len(qs) if isinstance(qs, list) else qs.count()
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_count'] = getattr(self, '_result_count', len(ctx['properties']))

        ctx['cities_all'] = Property.objects.filter(status='active').values_list('city', flat=True).distinct().order_by('city')
        ctx['types_all']  = [c[0] for c in Property.TYPE_CHOICES]

        g = self.request.GET
        ctx['selected_cities'] = g.getlist('city')
        ctx['selected_types'] = g.getlist('type')

        stats = Property.objects.filter(status='active').aggregate(
            min_price=Min('price_per_day'), max_price=Max('price_per_day'),
            min_beds=Min('beds'),            max_beds=Max('beds'),
        )
        ctx.update(stats)
        return ctx

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
