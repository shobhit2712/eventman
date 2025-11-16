from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """Event categories like Music, Sports, Theater, etc."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Venue(models.Model):
    """Physical locations where events take place"""
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="India")
    capacity = models.PositiveIntegerField()
    phone = models.CharField(max_length=20, default="9389761563")
    email = models.EmailField(default="techslave19@gmail.com")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='venues/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.city}"


class Event(models.Model):
    """Main event model"""
    EVENT_STATUS = (
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='events')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='events')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    
    event_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    doors_open = models.DateTimeField(null=True, blank=True)
    
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='events/banners/', blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=EVENT_STATUS, default='upcoming')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['event_date']
        indexes = [
            models.Index(fields=['event_date', 'status']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.title
    
    def is_upcoming(self):
        return self.event_date > timezone.now()
    
    def is_sold_out(self):
        return self.available_seats <= 0
    
    def get_booking_percentage(self):
        if self.total_seats > 0:
            return ((self.total_seats - self.available_seats) / self.total_seats) * 100
        return 0


class SeatCategory(models.Model):
    """Different seat categories for an event (VIP, Premium, General, etc.)"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='seat_categories')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    color_code = models.CharField(max_length=7, default="#007bff", help_text="Hex color code for seat map")
    
    class Meta:
        ordering = ['-price']
        unique_together = ['event', 'name']
    
    def __str__(self):
        return f"{self.event.title} - {self.name} (${self.price})"
    
    def is_available(self):
        return self.available_seats > 0


class Seat(models.Model):
    """Individual seats in a venue"""
    SEAT_STATUS = (
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('reserved', 'Reserved'),  # Temporarily held during booking process
        ('blocked', 'Blocked'),
    )
    
    seat_category = models.ForeignKey(SeatCategory, on_delete=models.CASCADE, related_name='seats')
    row = models.CharField(max_length=10)
    number = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=SEAT_STATUS, default='available')
    reserved_until = models.DateTimeField(null=True, blank=True)  # For temporary reservations
    
    class Meta:
        ordering = ['row', 'number']
        unique_together = ['seat_category', 'row', 'number']
    
    def __str__(self):
        return f"Row {self.row}, Seat {self.number}"
    
    def is_available(self):
        if self.status == 'reserved' and self.reserved_until:
            if timezone.now() > self.reserved_until:
                self.status = 'available'
                self.save()
        return self.status == 'available'


class EventImage(models.Model):
    """Additional images for events"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='events/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.event.title} - Image"
