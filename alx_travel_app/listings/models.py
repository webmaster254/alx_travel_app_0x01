from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()

class Listing(models.Model):
    """Model representing a property listing."""
    PROPERTY_TYPES = [
        ('APARTMENT', 'Apartment'),
        ('HOUSE', 'House'),
        ('VILLA', 'Villa'),
        ('CABIN', 'Cabin'),
        ('BEACH_HOUSE', 'Beach House'),
        ('OTHER', 'Other'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    max_guests = models.PositiveIntegerField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    amenities = models.JSONField(default=dict, blank=True)  # Stores amenities as key-value pairs
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'country']),
            models.Index(fields=['price_per_night']),
            models.Index(fields=['property_type']),
        ]

    def __str__(self):
        return f"{self.title} in {self.city}, {self.country}"

    def average_rating(self):
        """Calculate the average rating for this listing."""
        from django.db.models import Avg
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0


class Booking(models.Model):
    """Model representing a booking for a listing."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    number_of_guests = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out__gt=models.F('check_in')),
                name='check_out_after_check_in',
                violation_error_message='Check-out date must be after check-in date.'
            ),
        ]

    def __str__(self):
        return f"{self.guest.email}'s booking at {self.listing.title}"

    def is_available(self):
        """Check if the listing is available for the requested dates."""
        from django.db.models import Q
        
        conflicting_bookings = Booking.objects.filter(
            listing=self.listing,
            status__in=['CONFIRMED', 'PENDING'],
        ).exclude(id=self.id).filter(
            Q(check_in__lt=self.check_out) & Q(check_out__gt=self.check_in)
        )
        
        return not conflicting_bookings.exists()


class Review(models.Model):
    """Model representing a review for a listing."""
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['booking'],
                name='one_review_per_booking',
                violation_error_message='You have already reviewed this booking.'
            ),
            models.UniqueConstraint(
                fields=['reviewer', 'listing'],
                name='one_review_per_listing_per_user',
                condition=models.Q(booking__isnull=False),
                violation_error_message='You have already reviewed this listing.'
            ),
        ]

    def __str__(self):
        return f"{self.rating} stars by {self.reviewer.email} for {self.listing.title}"

    def save(self, *args, **kwargs):
        """Ensure the reviewer is the guest who made the booking."""
        if self.reviewer != self.booking.guest:
            raise ValueError("Only the guest who made the booking can leave a review.")
        if self.booking.status != 'COMPLETED':
            raise ValueError("Can only leave a review for completed bookings.")
        super().save(*args, **kwargs)
