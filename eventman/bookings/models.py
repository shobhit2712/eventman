from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from events.models import Event, Seat, SeatCategory
import uuid


class Booking(models.Model):
    """Main booking model for ticket purchases"""
    BOOKING_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    
    # Contact information
    contact_name = models.CharField(max_length=200)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    
    # Booking details
    num_tickets = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Timestamps
    booked_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Additional info
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-booked_at']
        indexes = [
            models.Index(fields=['booking_id']),
            models.Index(fields=['user', '-booked_at']),
        ]
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.event.title}"
    
    def confirm_booking(self):
        """Confirm the booking and mark seats as booked"""
        self.booking_status = 'confirmed'
        self.confirmed_at = timezone.now()
        self.save()
        
        # Mark all associated seats as booked
        for ticket in self.tickets.all():
            ticket.seat.status = 'booked'
            ticket.seat.save()
    
    def cancel_booking(self, reason=""):
        """Cancel booking and free up the seats"""
        self.booking_status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason
        self.save()
        
        # Free up seats
        for ticket in self.tickets.all():
            if ticket.seat.status == 'booked':
                ticket.seat.status = 'available'
                ticket.seat.save()
                
                # Update seat category available count
                seat_category = ticket.seat.seat_category
                seat_category.available_seats += 1
                seat_category.save()
        
        # Update event available seats
        self.event.available_seats += self.num_tickets
        self.event.save()


class Ticket(models.Model):
    """Individual ticket linked to a specific seat"""
    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='tickets')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='tickets')
    seat_category = models.ForeignKey(SeatCategory, on_delete=models.CASCADE, related_name='tickets')
    
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    is_checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['seat__row', 'seat__number']
    
    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.seat}"
    
    def check_in(self):
        """Mark ticket as checked in"""
        self.is_checked_in = True
        self.checked_in_at = timezone.now()
        self.save()


class Payment(models.Model):
    """Payment records for bookings"""
    PAYMENT_METHOD = (
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Wallet'),
    )
    
    payment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    transaction_id = models.CharField(max_length=200, blank=True)
    
    payment_status = models.CharField(max_length=20, choices=Booking.PAYMENT_STATUS, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Gateway details
    gateway_response = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount}"


class Cart(models.Model):
    """Temporary cart for holding seats during booking process"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        unique_together = ['user', 'event']
    
    def __str__(self):
        return f"Cart for {self.user.username} - {self.event.title}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at


class CartItem(models.Model):
    """Individual seats in a cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    seat_category = models.ForeignKey(SeatCategory, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cart', 'seat']
    
    def __str__(self):
        return f"{self.cart.user.username} - {self.seat}"
