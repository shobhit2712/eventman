from django.core.management.base import BaseCommand
from django.utils import timezone
from bookings.models import Cart
from events.models import Seat


class Command(BaseCommand):
    help = 'Cleanup expired carts and remove duplicate carts for users'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Step 1: Delete expired carts and release reserved seats
        expired_carts = Cart.objects.filter(expires_at__lt=now)
        expired_count = expired_carts.count()
        
        for cart in expired_carts:
            # Release seats reserved in expired carts
            for cart_item in cart.items.all():
                seat = cart_item.seat
                seat.is_reserved = False
                seat.reserved_until = None
                seat.save()
        
        expired_carts.delete()
        self.stdout.write(
            self.style.SUCCESS(f'✓ Deleted {expired_count} expired carts and released their seats')
        )
        
        # Step 2: Find and remove duplicate carts (keeping the most recent one per user-event)
        from django.db.models import Count
        
        # Find user-event combinations with multiple carts
        duplicates = Cart.objects.values('user', 'event').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        duplicate_removed = 0
        for dup in duplicates:
            # Get all carts for this user-event combination
            carts = Cart.objects.filter(
                user_id=dup['user'],
                event_id=dup['event']
            ).order_by('-created_at')
            
            # Keep the most recent, delete the rest
            keep_cart = carts.first()
            old_carts = carts.exclude(id=keep_cart.id)
            
            # Release seats from old carts
            for cart in old_carts:
                for cart_item in cart.items.all():
                    seat = cart_item.seat
                    seat.is_reserved = False
                    seat.reserved_until = None
                    seat.save()
            
            removed = old_carts.count()
            old_carts.delete()
            duplicate_removed += removed
            
            self.stdout.write(
                self.style.WARNING(
                    f'  Removed {removed} duplicate cart(s) for user {dup["user"]} '
                    f'and event {dup["event"]} (kept most recent)'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Removed {duplicate_removed} duplicate carts total')
        )
        
        # Step 3: Show remaining active carts
        active_carts = Cart.objects.filter(expires_at__gte=now).count()
        self.stdout.write(
            self.style.SUCCESS(f'✓ {active_carts} active cart(s) remaining')
        )
