import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker
from ...models import Listing, Booking, Review

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample data for the alx travel app'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5, help='Number of users to create')
        parser.add_argument('--listings', type=int, default=10, help='Number of listings to create')
        parser.add_argument('--bookings', type=int, default=20, help='Number of bookings to create')
        parser.add_argument('--reviews', type=int, default=15, help='Number of reviews to create')

    def handle(self, *args, **options):
        fake = Faker()
        Faker.seed(42)  # For consistent results

        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        # Create superuser if not exists
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                email='admin@example.com',
                username='admin',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user (admin@example.com / admin123)'))

        # Create regular users
        num_users = options['users']
        users = list(User.objects.all())
        
        if len(users) < num_users + 1:  # +1 for admin user
            for _ in range(num_users - len(users) + 1):
                first_name = fake.first_name()
                last_name = fake.last_name()
                email = fake.unique.email()
                user = User.objects.create_user(
                    username=email.split('@')[0],
                    email=email,
                    password='password123',
                    first_name=first_name,
                    last_name=last_name
                )
                users.append(user)
            self.stdout.write(self.style.SUCCESS(f'Created {num_users} regular users'))

        # Create listings
        num_listings = options['listings']
        property_types = [choice[0] for choice in Listing.PROPERTY_TYPES]
        cities = [
            ('Nairobi', 'Kenya'), ('Mombasa', 'Kenya'), ('Nakuru', 'Kenya'),
            ('Kisumu', 'Kenya'), ('Eldoret', 'Kenya'), ('Kigali', 'Rwanda'),
            ('Kampala', 'Uganda'), ('Arusha', 'Tanzania'), ('Zanzibar', 'Tanzania'),
            ('Cape Town', 'South Africa')
        ]
        
        listings = list(Listing.objects.all())
        if len(listings) < num_listings:
            for _ in range(num_listings - len(listings)):
                city, country = random.choice(cities)
                listing = Listing.objects.create(
                    title=fake.sentence(nb_words=4),
                    description=fake.paragraph(nb_sentences=6),
                    host=random.choice(users),
                    property_type=random.choice(property_types),
                    price_per_night=random.randint(20, 500),
                    bedrooms=random.randint(1, 6),
                    bathrooms=random.randint(1, 4),
                    max_guests=random.randint(2, 12),
                    address=fake.street_address(),
                    city=city,
                    country=country,
                    latitude=float(fake.latitude()),
                    longitude=float(fake.longitude()),
                    amenities={
                        'wifi': random.choice([True, False]),
                        'kitchen': random.choice([True, False]),
                        'parking': random.choice([True, False]),
                        'pool': random.choice([True, False]),
                        'air_conditioning': random.choice([True, False]),
                        'tv': random.choice([True, False]),
                    },
                    is_active=random.choice([True, True, True, False])  # 75% chance of being active
                )
                listings.append(listing)
            self.stdout.write(self.style.SUCCESS(f'Created {num_listings} property listings'))

        # Create bookings
        num_bookings = options['bookings']
        bookings = list(Booking.objects.all())
        booking_statuses = [status[0] for status in Booking.STATUS_CHOICES]
        
        if len(bookings) < num_bookings:
            today = timezone.now().date()
            for _ in range(num_bookings - len(bookings)):
                listing = random.choice(listings)
                guest = random.choice([u for u in users if u != listing.host])
                
                # Generate check-in date in the next 30 days
                check_in = today + timedelta(days=random.randint(1, 30))
                # Generate check-out date 1-14 days after check-in
                check_out = check_in + timedelta(days=random.randint(1, 14))
                
                # Calculate total price
                nights = (check_out - check_in).days
                total_price = nights * listing.price_per_night
                
                # Create booking
                booking = Booking.objects.create(
                    listing=listing,
                    guest=guest,
                    check_in=check_in,
                    check_out=check_out,
                    total_price=total_price,
                    status=random.choice(booking_statuses),
                    number_of_guests=random.randint(1, min(listing.max_guests, 6)),
                    special_requests=fake.sentence() if random.random() > 0.7 else ''
                )
                bookings.append(booking)
            self.stdout.write(self.style.SUCCESS(f'Created {num_bookings} bookings'))

        # Create reviews
        num_reviews = options['reviews']
        reviews = list(Review.objects.all())
        
        if len(reviews) < num_reviews:
            # Only consider completed bookings for reviews
            completed_bookings = [b for b in bookings if b.status == 'COMPLETED' and not hasattr(b, 'review')]
            
            for _ in range(min(num_reviews - len(reviews), len(completed_bookings))):
                booking = random.choice(completed_bookings)
                completed_bookings.remove(booking)
                
                review = Review.objects.create(
                    listing=booking.listing,
                    booking=booking,
                    reviewer=booking.guest,
                    rating=random.randint(1, 5),
                    comment=fake.paragraph(nb_sentences=3) if random.random() > 0.2 else ''
                )
                reviews.append(review)
            self.stdout.write(self.style.SUCCESS(f'Created {min(num_reviews, len(completed_bookings))} reviews'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))