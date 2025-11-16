from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import Category, Venue, Event, SeatCategory, Seat
from datetime import timedelta
from django.utils import timezone
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Creates sample data for EventMan application'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))

        # Create admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'techslave19@gmail.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('✓ Created admin user (username: admin, password: admin123)'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))

        # Create categories
        categories_data = [
            ('Music', 'Live music concerts and performances', 'fa-music'),
            ('Sports', 'Sporting events and tournaments', 'fa-futbol'),
            ('Theater', 'Theater plays and drama', 'fa-theater-masks'),
            ('Comedy', 'Stand-up comedy shows', 'fa-laugh'),
            ('Conference', 'Business conferences and seminars', 'fa-briefcase'),
            ('Festival', 'Cultural festivals and celebrations', 'fa-gift'),
        ]

        for name, desc, icon in categories_data:
            Category.objects.get_or_create(name=name, defaults={'description': desc, 'icon': icon})
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(categories_data)} categories'))

        # Create venues
        venues_data = [
            ('Grand Arena', '123 Main Street', 'Mumbai', 'Maharashtra', '400001', 5000),
            ('City Convention Center', '456 Park Avenue', 'Delhi', 'Delhi', '110001', 3000),
            ('Royal Theater', '789 Theater Road', 'Bangalore', 'Karnataka', '560001', 1500),
            ('Sports Stadium', '321 Stadium Lane', 'Chennai', 'Tamil Nadu', '600001', 10000),
            ('Music Hall', '654 Music Street', 'Kolkata', 'West Bengal', '700001', 2000),
        ]

        for name, address, city, state, zipcode, capacity in venues_data:
            Venue.objects.get_or_create(
                name=name,
                defaults={
                    'address': address,
                    'city': city,
                    'state': state,
                    'zipcode': zipcode,
                    'capacity': capacity,
                    'phone': '9389761563',
                    'email': 'techslave19@gmail.com',
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(venues_data)} venues'))

        # Get admin user
        admin_user = User.objects.get(username='admin')

        # Get categories and venues
        music_cat = Category.objects.get(name='Music')
        sports_cat = Category.objects.get(name='Sports')
        theater_cat = Category.objects.get(name='Theater')
        
        venue1 = Venue.objects.get(name='Grand Arena')
        venue3 = Venue.objects.get(name='Royal Theater')

        # Create events
        events_data = [
            {
                'title': 'Rock Music Festival 2025',
                'category': music_cat,
                'venue': venue1,
                'description': 'An electrifying night of rock music featuring top bands from around the country.',
                'event_date': timezone.now() + timedelta(days=30),
                'total_seats': 1000,
                'is_featured': True,
            },
            {
                'title': 'Cricket Championship Finals',
                'category': sports_cat,
                'venue': venue1,
                'description': 'Witness the most exciting cricket match of the season!',
                'event_date': timezone.now() + timedelta(days=15),
                'total_seats': 2000,
                'is_featured': True,
            },
            {
                'title': 'Shakespeare Hamlet Performance',
                'category': theater_cat,
                'venue': venue3,
                'description': 'A classic theatrical performance of Shakespeare masterpiece Hamlet.',
                'event_date': timezone.now() + timedelta(days=45),
                'total_seats': 500,
                'is_featured': False,
            },
        ]

        created_count = 0
        for event_data in events_data:
            slug = slugify(event_data['title'])
            event, created = Event.objects.get_or_create(
                slug=slug,
                defaults={
                    **event_data,
                    'organizer': admin_user,
                    'available_seats': event_data['total_seats'],
                    'status': 'upcoming',
                }
            )
            
            if created:
                created_count += 1
                # Create seat categories
                seat_categories_data = [
                    ('VIP', 2000, 100),
                    ('Premium', 1500, 200),
                    ('General', 1000, event_data['total_seats'] - 300),
                ]
                
                for cat_name, price, total in seat_categories_data:
                    seat_cat = SeatCategory.objects.create(
                        event=event,
                        name=cat_name,
                        price=price,
                        total_seats=total,
                        available_seats=total,
                    )
                    
                    # Create seats
                    rows = ['A', 'B', 'C', 'D', 'E']
                    seats_per_row = min(20, total // len(rows))
                    
                    for row in rows:
                        for num in range(1, seats_per_row + 1):
                            Seat.objects.create(
                                seat_category=seat_cat,
                                row=row,
                                number=str(num),
                                status='available',
                            )

        self.stdout.write(self.style.SUCCESS(f'✓ Created {created_count} events with seats'))
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.WARNING('\nAdmin Login:'))
        self.stdout.write('Username: admin')
        self.stdout.write('Password: admin123')
