from rest_framework import serializers
from .models import Listing, Booking, Review
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for the Review model"""
    reviewer = UserSerializer(read_only=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer',
        queryset=User.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = Review
        fields = [
            'id', 'booking', 'reviewer', 'reviewer_id', 'rating', 
            'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
        extra_kwargs = {
            'booking': {'required': True}
        }

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

class ListingSerializer(serializers.ModelSerializer):
    """Serializer for the Listing model"""
    host = UserSerializer(read_only=True)
    host_id = serializers.PrimaryKeyRelatedField(
        source='host',
        queryset=User.objects.all(),
        write_only=True,
        required=False
    )
    average_rating = serializers.FloatField(read_only=True)
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'host', 'host_id', 'property_type',
            'price_per_night', 'bedrooms', 'bathrooms', 'max_guests',
            'address', 'city', 'country', 'latitude', 'longitude',
            'amenities', 'is_active', 'created_at', 'updated_at',
            'average_rating', 'is_available'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at', 'average_rating')
        extra_kwargs = {
            'amenities': {'required': False, 'default': dict}
        }

    def get_is_available(self, obj):
        request = self.context.get('request')
        if not request or 'check_in' not in request.query_params or 'check_out' not in request.query_params:
            return None
            
        check_in = request.query_params['check_in']
        check_out = request.query_params['check_out']
        
        # simplified availability check 
        return not obj.bookings.filter(
            check_in__lt=check_out,
            check_out__gt=check_in,
            status__in=['CONFIRMED', 'PENDING']
        ).exists()

class BookingSerializer(serializers.ModelSerializer):
    """Serializer for the Booking model"""
    guest = UserSerializer(read_only=True)
    guest_id = serializers.PrimaryKeyRelatedField(
        source='guest',
        queryset=User.objects.all(),
        write_only=True
    )
    listing = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all())
    listing_details = ListingSerializer(source='listing', read_only=True)
    status = serializers.ChoiceField(
        choices=Booking.STATUS_CHOICES,
        default='PENDING',
        read_only=True
    )
    review = ReviewSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_details', 'guest', 'guest_id',
            'check_in', 'check_out', 'total_price', 'status',
            'number_of_guests', 'special_requests', 'created_at',
            'updated_at', 'review'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at', 'review')

    def validate(self, data):
        """
        Check that check_in is before check_out and validate booking dates.
        """
        if data['check_in'] >= data['check_out']:
            raise serializers.ValidationError({"check_out": "Check-out date must be after check-in date."})
        
        # Check if the listing is available for the requested dates
        listing = data['listing']
        check_in = data['check_in']
        check_out = data['check_out']
        
        conflicting_bookings = listing.bookings.filter(
            status__in=['CONFIRMED', 'PENDING'],
            check_in__lt=check_out,
            check_out__gt=check_in
        )
        
        # Exclude current instance if updating
        if self.instance:
            conflicting_bookings = conflicting_bookings.exclude(id=self.instance.id)
        
        if conflicting_bookings.exists():
            raise serializers.ValidationError(
                "This listing is not available for the selected dates."
            )
            
        # Check if number of guests exceeds listing capacity
        if data['number_of_guests'] > listing.max_guests:
            raise serializers.ValidationError({
                'number_of_guests': f'Maximum {listing.max_guests} guests allowed for this listing.'
            })
            
        return data

    def create(self, validated_data):
        # Calculate total price
        days = (validated_data['check_out'] - validated_data['check_in']).days
        validated_data['total_price'] = days * validated_data['listing'].price_per_night
        return super().create(validated_data)

class BookingStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating booking status"""
    class Meta:
        model = Booking
        fields = ['status']
        extra_kwargs = {
            'status': {'required': True}
        }

    def validate_status(self, value):
        valid_transitions = {
            'PENDING': ['CONFIRMED', 'CANCELLED'],
            'CONFIRMED': ['COMPLETED', 'CANCELLED'],
            'COMPLETED': [],
            'CANCELLED': []
        }
        
        current_status = self.instance.status
        if value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot change status from {current_status} to {value}"
            )
        return value
