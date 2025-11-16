from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('select-seats/<slug:event_slug>/', views.select_seats, name='select_seats'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirm/<uuid:booking_id>/', views.booking_confirmation, name='confirmation'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking-detail/<uuid:booking_id>/', views.booking_detail, name='booking_detail'),
    path('cancel-booking/<uuid:booking_id>/', views.cancel_booking, name='cancel_booking'),
]
