from django.contrib import admin
from .models import Listing, Booking, Review
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'host', 'property_type', 'city', 'country', 'price_per_night', 'is_active', 'created_at')
    list_filter = ('property_type', 'city', 'country', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'address', 'city', 'country')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at', 'average_rating_display')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'host', 'property_type', 'price_per_night')
        }),
        ('Property Details', {
            'fields': ('bedrooms', 'bathrooms', 'max_guests', 'amenities')
        }),
        ('Location', {
            'fields': ('address', 'city', 'country', 'latitude', 'longitude')
        }),
        ('Status & Dates', {
            'fields': ('is_active', 'created_at', 'updated_at', 'average_rating_display')
        }),
    )

    def average_rating_display(self, obj):
        return f"{obj.average_rating():.1f} / 5.0"
    average_rating_display.short_description = 'Average Rating'


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    can_delete = False
    show_change_link = True


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'guest', 'check_in', 'check_out', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'check_in', 'check_out', 'created_at')
    search_fields = ('listing__title', 'guest__email', 'guest__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_select_related = ('listing', 'guest')
    
    fieldsets = (
        ('Booking Details', {
            'fields': ('listing', 'guest', 'number_of_guests', 'status', 'total_price')
        }),
        ('Dates', {
            'fields': ('check_in', 'check_out')
        }),
        ('Additional Information', {
            'fields': ('special_requests', 'created_at', 'updated_at')
        }),
    )
    
    def view_listing_link(self, obj):
        url = reverse('admin:listings_listing_change', args=[obj.listing.id])
        return format_html('<a href="{}">{}</a>', url, obj.listing.title)
    view_listing_link.short_description = 'Listing'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('listing__title', 'reviewer__email', 'reviewer__username', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('listing', 'reviewer', 'booking')
    
    fieldsets = (
        ('Review Details', {
            'fields': ('listing', 'booking', 'reviewer', 'rating')
        }),
        ('Content', {
            'fields': ('comment',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def view_booking_link(self, obj):
        if obj.booking:
            url = reverse('admin:listings_booking_change', args=[obj.booking.id])
            return format_html('<a href="{}">Booking #{}</a>', url, obj.booking.id)
        return "-"
    view_booking_link.short_description = 'Booking'
