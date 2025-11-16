from django.contrib import admin
from .models import Category, Venue, Event, SeatCategory, Seat, EventImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'created_at')
    search_fields = ('name',)


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'capacity', 'phone')
    list_filter = ('city', 'state', 'country')
    search_fields = ('name', 'city', 'address')


class SeatCategoryInline(admin.TabularInline):
    model = SeatCategory
    extra = 1


class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'venue', 'event_date', 'status', 'available_seats', 'is_featured')
    list_filter = ('status', 'category', 'is_featured', 'event_date')
    search_fields = ('title', 'description', 'venue__name')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'event_date'
    inlines = [SeatCategoryInline, EventImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'category', 'organizer')
        }),
        ('Venue & Dates', {
            'fields': ('venue', 'event_date', 'end_date', 'doors_open')
        }),
        ('Media', {
            'fields': ('image', 'banner_image')
        }),
        ('Seating', {
            'fields': ('total_seats', 'available_seats')
        }),
        ('Status', {
            'fields': ('status', 'is_featured', 'is_active')
        }),
    )


@admin.register(SeatCategory)
class SeatCategoryAdmin(admin.ModelAdmin):
    list_display = ('event', 'name', 'price', 'available_seats', 'total_seats')
    list_filter = ('event',)
    search_fields = ('name', 'event__title')


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('seat_category', 'row', 'number', 'status', 'reserved_until')
    list_filter = ('status', 'seat_category')
    search_fields = ('row', 'number')


@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ('event', 'caption', 'uploaded_at')
    list_filter = ('event',)
    search_fields = ('event__title', 'caption')
