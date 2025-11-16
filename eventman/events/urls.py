from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.event_list, name='event_list'),
    path('event/<slug:slug>/', views.event_detail, name='event_detail'),
    path('category/<int:category_id>/', views.events_by_category, name='events_by_category'),
    path('search/', views.search_events, name='search_events'),
    path('api/check-seats/<int:event_id>/', views.check_seat_availability, name='check_seats'),
]
