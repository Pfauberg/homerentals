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
