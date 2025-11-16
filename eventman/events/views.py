from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from .models import Event, Category, Venue, SeatCategory, Seat


def home(request):
    """Homepage with featured and upcoming events"""
    featured_events = Event.objects.filter(
        is_featured=True, 
        is_active=True,
        event_date__gte=timezone.now()
    )[:6]
    
    upcoming_events = Event.objects.filter(
        is_active=True,
        event_date__gte=timezone.now()
    ).order_by('event_date')[:8]
    
    categories = Category.objects.all()
    
    context = {
        'featured_events': featured_events,
        'upcoming_events': upcoming_events,
        'categories': categories,
    }
    return render(request, 'events/home.html', context)


def event_list(request):
    """List all events with filtering options"""
    events = Event.objects.filter(
        is_active=True,
        event_date__gte=timezone.now()
    )
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        events = events.filter(category_id=category_id)
    
    # Filter by city
    city = request.GET.get('city')
    if city:
        events = events.filter(venue__city__icontains=city)
    
    # Sort
    sort_by = request.GET.get('sort', 'date')
    if sort_by == 'date':
        events = events.order_by('event_date')
    elif sort_by == 'popularity':
        events = events.order_by('-available_seats')
    
    categories = Category.objects.all()
    cities = Venue.objects.values_list('city', flat=True).distinct()
    
    context = {
        'events': events,
        'categories': categories,
        'cities': cities,
        'selected_category': category_id,
        'selected_city': city,
    }
    return render(request, 'events/event_list.html', context)


def event_detail(request, slug):
    """Detailed view of a single event"""
    event = get_object_or_404(Event, slug=slug, is_active=True)
    seat_categories = event.seat_categories.all()
    
    context = {
        'event': event,
        'seat_categories': seat_categories,
    }
    return render(request, 'events/event_detail.html', context)


def events_by_category(request, category_id):
    """List events filtered by category"""
    category = get_object_or_404(Category, id=category_id)
    events = Event.objects.filter(
        category=category,
        is_active=True,
        event_date__gte=timezone.now()
    ).order_by('event_date')
    
    context = {
        'category': category,
        'events': events,
    }
    return render(request, 'events/events_by_category.html', context)


def search_events(request):
    """Search events by title, description, or venue"""
    query = request.GET.get('q', '')
    events = Event.objects.none()
    
    if query:
        events = Event.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(venue__name__icontains=query) |
            Q(venue__city__icontains=query),
            is_active=True,
            event_date__gte=timezone.now()
        ).order_by('event_date')
    
    context = {
        'events': events,
        'query': query,
    }
    return render(request, 'events/search_results.html', context)


def check_seat_availability(request, event_id):
    """AJAX endpoint to check real-time seat availability"""
    try:
        event = Event.objects.get(id=event_id)
        seat_categories = event.seat_categories.all()
        
        data = {
            'event_id': event.id,
            'total_available': event.available_seats,
            'categories': []
        }
        
        for cat in seat_categories:
            data['categories'].append({
                'id': cat.id,
                'name': cat.name,
                'price': str(cat.price),
                'available': cat.available_seats,
                'total': cat.total_seats,
            })
        
        return JsonResponse(data)
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)
