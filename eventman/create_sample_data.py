"""
Sample data creation script for EventMan
Run with: python manage.py shell < create_sample_data.py
"""

from django.contrib.auth.models import User
from events.models import Category, Venue, Event, SeatCategory, Seat
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.text import slugify

print("Creating sample data...")

# Create a superuser if not exists
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'techslave19@gmail.com', 'admin123')
    print("✓ Created admin user (username: admin, password: admin123)")

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
print(f"✓ Created {len(categories_data)} categories")

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
print(f"✓ Created {len(venues_data)} venues")

# Get admin user for organizer
admin_user = User.objects.get(username='admin')

# Create events
music_cat = Category.objects.get(name='Music')
sports_cat = Category.objects.get(name='Sports')
theater_cat = Category.objects.get(name='Theater')

venue1 = Venue.objects.get(name='Grand Arena')
venue2 = Venue.objects.get(name='City Convention Center')
venue3 = Venue.objects.get(name='Royal Theater')

events_data = [
    {
        'title': 'Rock Music Festival 2025',
        'category': music_cat,
        'venue': venue1,
        'description': 'An electrifying night of rock music featuring top bands from around the country. Experience the best of rock with amazing performances, stunning visuals, and an unforgettable atmosphere.',
        'event_date': timezone.now() + timedelta(days=30),
        'total_seats': 1000,
        'is_featured': True,
    },
    {
        'title': 'Cricket Championship Finals',
        'category': sports_cat,
        'venue': venue1,
        'description': 'Witness the most exciting cricket match of the season! Two top teams battle it out for the championship title. Don\'t miss the action-packed finale.',
        'event_date': timezone.now() + timedelta(days=15),
        'total_seats': 2000,
        'is_featured': True,
    },
    {
        'title': 'Shakespeare\'s Hamlet',
        'category': theater_cat,
        'venue': venue3,
        'description': 'A classic theatrical performance of Shakespeare\'s masterpiece Hamlet. Experience the timeless tragedy brought to life by talented actors.',
        'event_date': timezone.now() + timedelta(days=45),
        'total_seats': 500,
        'is_featured': False,
    },
]

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
        # Create seat categories for each event
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
            
            # Create seats for this category
            rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
            seats_per_row = total // len(rows)
            
            for row in rows:
                for num in range(1, seats_per_row + 1):
                    Seat.objects.create(
                        seat_category=seat_cat,
                        row=row,
                        number=str(num),
                        status='available',
                    )

print(f"✓ Created {len(events_data)} events with seat categories and seats")

print("\n" + "="*50)
print("Sample data created successfully!")
print("="*50)
print("\nAdmin Login:")
print("Username: admin")
print("Password: admin123")
print("\nYou can now:")
print("1. Access admin panel: http://127.0.0.1:8000/admin/")
print("2. Browse events: http://127.0.0.1:8000/")
print("3. Create more events and manage bookings")
