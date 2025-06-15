# Listings App

This is the core application for managing property listings, bookings, and reviews in the ALX Travel App.

## Models

### Listing
Represents a property available for booking with the following fields:
- `title`: Property title
- `description`: Detailed property description
- `host`: ForeignKey to User model (property owner)
- `property_type`: Type of property (e.g., Apartment, House, Villa)
- `price_per_night`: Price per night in USD
- `bedrooms`: Number of bedrooms
- `bathrooms`: Number of bathrooms
- `max_guests`: Maximum number of guests
- `location`: Physical address
- `amenities`: JSON field for property amenities
- `status`: Current status (active, inactive, booked)
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

### Booking
Manages property reservations:
- `listing`: ForeignKey to Listing
- `guest`: ForeignKey to User (person making the booking)
- `check_in`: Check-in date
- `check_out`: Check-out date
- `status`: Booking status (pending, confirmed, cancelled, completed)
- `total_price`: Total booking cost
- `special_requests`: Any special requirements
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

### Review
Handles user reviews for properties:
- `booking`: OneToOneField to Booking
- `listing`: ForeignKey to Listing
- `reviewer`: ForeignKey to User (person writing the review)
- `rating`: Rating from 1 to 5
- `comment`: Review text
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

## Management Commands

### Seed Command
Populates the database with sample data for testing and development.

**Usage:**
```bash
python manage.py seed [--users N] [--listings N] [--bookings N] [--reviews N]
```

**Options:**
- `--users`: Number of users to create (default: 5)
- `--listings`: Number of listings to create (default: 10)
- `--bookings`: Number of bookings to create (default: 20)
- `--reviews`: Number of reviews to create (default: 15)
- `--clear`: Clear existing data before seeding (default: False)

**Examples:**
1. Seed with default values:
   ```bash
   python manage.py seed
   ```

2. Create specific number of records:
   ```bash
   python manage.py seed --users 3 --listings 5 --bookings 15 --reviews 10
   ```

3. Clear existing data and seed:
   ```bash
   python manage.py seed --clear
   ```

The seed command ensures data consistency by:
- Creating users with realistic names and emails
- Generating listings with diverse property types and amenities
- Creating valid bookings with proper date ranges
- Adding reviews only for completed bookings

## API Endpoints

### Listings
- `GET /api/listings/`: List all active listings
- `POST /api/listings/`: Create a new listing (authenticated)
- `GET /api/listings/{id}/`: Get listing details
- `PUT /api/listings/{id}/`: Update a listing (owner only)
- `DELETE /api/listings/{id}/`: Delete a listing (owner only)

### Bookings
- `GET /api/bookings/`: List user's bookings
- `POST /api/bookings/`: Create a new booking
- `GET /api/bookings/{id}/`: Get booking details
- `PATCH /api/bookings/{id}/status/`: Update booking status (host/owner only)

### Reviews
- `GET /api/listings/{id}/reviews/`: Get reviews for a listing
- `POST /api/listings/{id}/reviews/`: Add a review (authenticated users only)

## Running Tests

To run the test suite:
```bash
python manage.py test listings
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
