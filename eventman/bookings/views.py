from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import math
from events.models import Event, Seat, SeatCategory
from .models import Booking, Ticket, Cart, CartItem, Payment
import uuid


@login_required
def select_seats(request, event_slug):
    """Seat selection page with interactive seat map"""
    event = get_object_or_404(Event, slug=event_slug, is_active=True)
    seat_categories = event.seat_categories.all()
    
    # Get or create cart for this user and event
    cart, created = Cart.objects.get_or_create(
        user=request.user,
        event=event,
        defaults={'expires_at': timezone.now() + timedelta(minutes=15)}
    )
    
    # If cart exists and not expired, extend expiration and reserved holds
    if not created and not cart.is_expired():
        cart.expires_at = timezone.now() + timedelta(minutes=15)
        cart.save()
        # Extend reserved_until on all reserved seats in this cart
        for item in cart.items.all():
            if item.seat.status == 'reserved':
                item.seat.reserved_until = cart.expires_at
                item.seat.save()
    
    # Check if cart is expired
    if cart.is_expired():
        # Release reserved seats
        for item in cart.items.all():
            item.seat.status = 'available'
            item.seat.reserved_until = None
            item.seat.save()
        cart.items.all().delete()
        cart.expires_at = timezone.now() + timedelta(minutes=15)
        cart.save()
    
    context = {
        'event': event,
        'seat_categories': seat_categories,
        'cart': cart,
    }
    return render(request, 'bookings/select_seats.html', context)


@login_required
def add_to_cart(request):
    """Add selected seats to cart via AJAX"""
    if request.method == 'POST':
        seat_ids = request.POST.getlist('seat_ids[]')
        event_id = request.POST.get('event_id')
        
        try:
            event = Event.objects.get(id=event_id)
            
            # Get or create cart for this user and event (ensures only one cart per user-event)
            cart, created = Cart.objects.get_or_create(
                user=request.user,
                event=event,
                defaults={'expires_at': timezone.now() + timedelta(minutes=15)}
            )
            
            # Clear existing items from cart and release their seats
            for item in cart.items.all():
                seat = item.seat
                seat.status = 'available'
                seat.reserved_until = None
                seat.save()
            cart.items.all().delete()
            
            # Update cart expiration
            cart.expires_at = timezone.now() + timedelta(minutes=15)
            cart.save()
            
            with transaction.atomic():
                for seat_id in seat_ids:
                    seat = Seat.objects.select_for_update().get(id=seat_id)
                    
                    if seat.is_available():
                        # Reserve the seat
                        seat.status = 'reserved'
                        seat.reserved_until = cart.expires_at
                        seat.save()
                        
                        # Add to cart
                        CartItem.objects.create(
                            cart=cart,
                            seat=seat,
                            seat_category=seat.seat_category
                        )
                    else:
                        return JsonResponse({
                            'success': False,
                            'message': f'Seat {seat} is no longer available'
                        })
            
            return JsonResponse({
                'success': True,
                'message': 'Seats added to cart',
                'cart_count': cart.items.count()
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def view_cart(request):
    """View shopping cart"""
    # Get the most recent active cart for this user
    cart = Cart.objects.filter(
        user=request.user, 
        event__is_active=True
    ).order_by('-created_at').first()
    
    if not cart:
        messages.info(request, 'Your cart is empty.')
        return redirect('events:event_list')
    
    if cart.is_expired():
        messages.warning(request, 'Your cart has expired. Please select seats again.')
        # Release seats
        for item in cart.items.all():
            item.seat.status = 'available'
            item.seat.reserved_until = None
            item.seat.save()
        cart.items.all().delete()
        # Reset the cart window and send user back to seat selection for the event
        cart.expires_at = timezone.now() + timedelta(minutes=15)
        cart.save()
        return redirect('bookings:select_seats', event_slug=cart.event.slug)

    # Extend cart expiration when viewing the cart to give users full time window
    cart.expires_at = timezone.now() + timedelta(minutes=15)
    cart.save()
    # Extend reserved_until for seats in this cart
    for item in cart.items.all():
        if item.seat.status == 'reserved':
            item.seat.reserved_until = cart.expires_at
            item.seat.save()
    
    items = cart.items.all()
    total = sum(item.seat_category.price for item in items)
    
    # Compute remaining time in minutes (rounded up, minimum 1 minute)
    remaining_delta = cart.expires_at - timezone.now()
    remaining_minutes = max(1, math.ceil(remaining_delta.total_seconds() / 60))

    context = {
        'cart': cart,
        'items': items,
        'total': total,
        'time_remaining': remaining_minutes,
    }
    return render(request, 'bookings/cart.html', context)


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    try:
        item = CartItem.objects.get(id=item_id, cart__user=request.user)
        seat = item.seat
        seat.status = 'available'
        seat.reserved_until = None
        seat.save()
        item.delete()
        messages.success(request, 'Seat removed from cart.')
    except CartItem.DoesNotExist:
        messages.error(request, 'Item not found.')
    
    return redirect('bookings:view_cart')


@login_required
def checkout(request):
    """Checkout and complete booking"""
    # Get the most recent active cart for this user
    cart = Cart.objects.filter(
        user=request.user,
        event__is_active=True
    ).order_by('-created_at').first()
    
    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('events:event_list')
    
    if cart.is_expired():
        messages.error(request, 'Your cart has expired. Please select seats again.')
        # Release seats
        for item in cart.items.all():
            item.seat.status = 'available'
            item.seat.reserved_until = None
            item.seat.save()
        cart.items.all().delete()
        cart.expires_at = timezone.now() + timedelta(minutes=15)
        cart.save()
        return redirect('bookings:select_seats', event_slug=cart.event.slug)

    # Extend cart expiration and reserved holds when entering checkout
    cart.expires_at = timezone.now() + timedelta(minutes=15)
    cart.save()
    for item in cart.items.all():
        if item.seat.status == 'reserved':
            item.seat.reserved_until = cart.expires_at
            item.seat.save()
    
    if request.method == 'POST':
        contact_name = request.POST.get('contact_name')
        contact_email = request.POST.get('contact_email')
        contact_phone = request.POST.get('contact_phone')
        payment_method = request.POST.get('payment_method')
        
        items = cart.items.all()
        total_amount = sum(item.seat_category.price for item in items)
        
        with transaction.atomic():
            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                event=cart.event,
                contact_name=contact_name,
                contact_email=contact_email,
                contact_phone=contact_phone,
                num_tickets=items.count(),
                total_amount=total_amount,
                booking_status='confirmed',
                payment_status='paid',
                confirmed_at=timezone.now()
            )
            
            # Create tickets
            for item in items:
                Ticket.objects.create(
                    booking=booking,
                    seat=item.seat,
                    seat_category=item.seat_category,
                    price_paid=item.seat_category.price
                )
                
                # Mark seat as booked
                item.seat.status = 'booked'
                item.seat.reserved_until = None
                item.seat.save()
                
                # Update seat category available count
                seat_cat = item.seat_category
                seat_cat.available_seats -= 1
                seat_cat.save()
            
            # Update event available seats
            cart.event.available_seats -= items.count()
            cart.event.save()
            
            # Create payment record
            Payment.objects.create(
                booking=booking,
                amount=total_amount,
                payment_method=payment_method,
                transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
                payment_status='paid'
            )
            
            # Clear cart
            cart.delete()
            
            messages.success(request, 'Booking confirmed successfully!')
            return redirect('bookings:confirmation', booking_id=booking.booking_id)
    
    items = cart.items.all()
    total = sum(item.seat_category.price for item in items)
    
    context = {
        'cart': cart,
        'items': items,
        'total': total,
    }
    return render(request, 'bookings/checkout.html', context)


@login_required
def booking_confirmation(request, booking_id):
    """Show booking confirmation"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    tickets = booking.tickets.all()
    
    context = {
        'booking': booking,
        'tickets': tickets,
    }
    return render(request, 'bookings/confirmation.html', context)


@login_required
def my_bookings(request):
    """List user's bookings"""
    bookings = Booking.objects.filter(user=request.user).order_by('-booked_at')
    
    context = {
        'bookings': bookings,
    }
    return render(request, 'bookings/my_bookings.html', context)


@login_required
def booking_detail(request, booking_id):
    """Detailed view of a booking"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    tickets = booking.tickets.all()
    
    context = {
        'booking': booking,
        'tickets': tickets,
    }
    return render(request, 'bookings/booking_detail.html', context)


@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    
    if booking.booking_status == 'cancelled':
        messages.info(request, 'This booking is already cancelled.')
        return redirect('bookings:booking_detail', booking_id=booking_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        booking.cancel_booking(reason)
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('bookings:my_bookings')
    
    context = {
        'booking': booking,
    }
    return render(request, 'bookings/cancel_booking.html', context)
