from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'listings', views.ListingViewSet, basename='listing')
router.register(r'bookings', views.BookingViewSet, basename='booking')

app_name = 'listings'

# The API URLs are now determined automatically by the router
urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    
    # Custom actions
    path('bookings/<int:pk>/update_status/', 
         views.BookingViewSet.as_view({'patch': 'update_status'}), 
         name='booking-update-status'),
]
