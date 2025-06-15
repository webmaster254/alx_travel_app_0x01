from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Listing, Booking, Review
from .serializers import (
    ListingSerializer, 
    BookingSerializer, 
    BookingStatusUpdateSerializer
)

class ListingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows listings to be viewed or edited.
    """
    queryset = Listing.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = ListingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'bedrooms', 'bathrooms', 'city', 'country']
    search_fields = ['title', 'description', 'address', 'city', 'country']
    ordering_fields = ['price_per_night', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Set the host to the current user when creating a new listing.
        """
        serializer.save(host=self.request.user)

    def perform_update(self, serializer):
        """
        Ensure only the host or admin can update the listing.
        """
        if self.get_object().host != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("You do not have permission to edit this listing.")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Instead of deleting, set is_active to False.
        """
        instance.is_active = False
        instance.save()


class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows bookings to be viewed or edited.
    """
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['listing', 'status', 'guest']
    ordering_fields = ['check_in', 'check_out', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return bookings for the current user, or all bookings for staff.
        """
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all().order_by('-created_at')
        return Booking.objects.filter(guest=user).order_by('-created_at')

    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action == 'update_status':
            return BookingStatusUpdateSerializer
        return BookingSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy', 'update_status']:
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Set the guest to the current user when creating a new booking.
        """
        serializer.save(guest=self.request.user)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Custom action to update booking status.
        """
        booking = self.get_object()
        serializer = self.get_serializer(booking, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
