from django.contrib import admin
from .models import Booking, Ticket, Payment, Cart, CartItem


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    readonly_fields = ('ticket_id', 'price_paid', 'is_checked_in', 'checked_in_at')


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('payment_id', 'transaction_id', 'created_at')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'event', 'num_tickets', 'total_amount', 
                    'booking_status', 'payment_status', 'booked_at')
    list_filter = ('booking_status', 'payment_status', 'booked_at')
    search_fields = ('booking_id', 'user__username', 'event__title', 'contact_email')
    readonly_fields = ('booking_id', 'booked_at', 'confirmed_at', 'cancelled_at')
    date_hierarchy = 'booked_at'
    inlines = [TicketInline, PaymentInline]
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_id', 'user', 'event', 'num_tickets', 'total_amount')
        }),
        ('Contact Details', {
            'fields': ('contact_name', 'contact_email', 'contact_phone')
        }),
        ('Status', {
            'fields': ('booking_status', 'payment_status')
        }),
        ('Timestamps', {
            'fields': ('booked_at', 'confirmed_at', 'cancelled_at')
        }),
        ('Additional Info', {
            'fields': ('notes', 'cancellation_reason'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'booking', 'seat', 'seat_category', 'price_paid', 'is_checked_in')
    list_filter = ('is_checked_in', 'seat_category')
    search_fields = ('ticket_id', 'booking__booking_id')
    readonly_fields = ('ticket_id', 'checked_in_at')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'booking', 'amount', 'payment_method', 'payment_status', 'created_at')
    list_filter = ('payment_status', 'payment_method', 'created_at')
    search_fields = ('payment_id', 'transaction_id', 'booking__booking_id')
    readonly_fields = ('payment_id', 'created_at', 'updated_at')


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'created_at', 'expires_at', 'is_expired')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('user__username', 'event__title')
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'seat', 'seat_category', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('cart__user__username', 'seat__row', 'seat__number')
