from django.core.management.base import BaseCommand
from events.models import Event, SeatCategory, Seat
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Add seats to an existing event'

    def add_arguments(self, parser):
        parser.add_argument('event_slug', type=str, help='Slug of the event (e.g., tech-meet)')

    def handle(self, *args, **options):
        event_slug = options['event_slug']
        
        try:
            event = Event.objects.get(slug=event_slug)
        except Event.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Event with slug "{event_slug}" not found'))
            self.stdout.write(self.style.WARNING('Available events:'))
            for e in Event.objects.all():
                self.stdout.write(f'  - {e.slug}')
            return

        # Check if event already has seat categories
        if event.seat_categories.exists():
            self.stdout.write(self.style.WARNING(f'Event "{event.title}" already has seat categories!'))
            response = input('Do you want to add more seats? (yes/no): ')
            if response.lower() != 'yes':
                return

        self.stdout.write(self.style.SUCCESS(f'Adding seats to event: {event.title}'))

        # Ask for seat configuration
        self.stdout.write('\nSeat Category Configuration:')
        
        # Default configuration
        seat_configs = [
            {'name': 'VIP', 'price': 2000, 'seats': 100},
            {'name': 'Premium', 'price': 1500, 'seats': 200},
            {'name': 'General', 'price': 1000, 'seats': 200},
        ]

        total_new_seats = 0
        
        for config in seat_configs:
            self.stdout.write(f'\nCreating {config["name"]} category...')
            
            # Create or get seat category
            seat_cat, created = SeatCategory.objects.get_or_create(
                event=event,
                name=config['name'],
                defaults={
                    'price': config['price'],
                    'total_seats': config['seats'],
                    'available_seats': config['seats'],
                    'description': f'{config["name"]} seating area',
                }
            )
            
            if not created:
                self.stdout.write(self.style.WARNING(f'  {config["name"]} category already exists'))
                continue
            
            # Create individual seats
            rows = ['A', 'B', 'C', 'D', 'E']
            seats_per_row = config['seats'] // len(rows)
            
            seat_count = 0
            for row in rows:
                for num in range(1, seats_per_row + 1):
                    Seat.objects.create(
                        seat_category=seat_cat,
                        row=row,
                        number=str(num),
                        status='available',
                    )
                    seat_count += 1
            
            total_new_seats += seat_count
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created {seat_count} seats in {config["name"]}'))

        # Update event totals if needed
        total_seats_in_categories = sum(cat.total_seats for cat in event.seat_categories.all())
        if event.total_seats < total_seats_in_categories:
            event.total_seats = total_seats_in_categories
            event.available_seats = total_seats_in_categories
            event.save()
            self.stdout.write(self.style.WARNING(f'\nUpdated event total_seats to {total_seats_in_categories}'))

        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully added {total_new_seats} seats to "{event.title}"'))
        self.stdout.write(self.style.SUCCESS(f'Total seat categories: {event.seat_categories.count()}'))
        self.stdout.write(self.style.SUCCESS('\nYou can now book tickets for this event!'))
