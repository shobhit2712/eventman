from django.core.management.base import BaseCommand
from bookings.models import Cart
from django.utils import timezone


class Command(BaseCommand):
    help = 'Clean up duplicate and expired carts'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Cleaning up carts...'))
        
        # Delete expired carts
        expired_count = 0
        for cart in Cart.objects.all():
            if cart.is_expired():
                # Release reserved seats
                for item in cart.items.all():
                    item.seat.status = 'available'
                    item.seat.reserved_until = None
                    item.seat.save()
                cart.delete()
                expired_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Deleted {expired_count} expired carts'))
        
        # Find and keep only the most recent cart per user per event
        from django.db.models import Count
        
        # Find users with duplicate carts
        duplicates = Cart.objects.values('user', 'event').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        deleted_duplicates = 0
        for dup in duplicates:
            # Get all carts for this user-event combo
            carts = Cart.objects.filter(
                user_id=dup['user'],
                event_id=dup['event']
            ).order_by('-created_at')
            
            # Keep the most recent one, delete the rest
            carts_to_delete = carts[1:]
            for cart in carts_to_delete:
                # Release seats
                for item in cart.items.all():
                    item.seat.status = 'available'
                    item.seat.reserved_until = None
                    item.seat.save()
                cart.delete()
                deleted_duplicates += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Deleted {deleted_duplicates} duplicate carts'))
        
        remaining = Cart.objects.count()
        self.stdout.write(self.style.SUCCESS(f'\n✓ Cleanup complete! {remaining} active carts remaining'))
