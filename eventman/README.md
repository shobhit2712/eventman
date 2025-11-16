# EventMan - Event Management & Ticket Booking Platform

A comprehensive Django-based event management and ticket booking system with real-time seat availability updates.

## Features

- **Event Discovery**: Browse and search events by category, city, or keywords
- **Real-Time Seat Booking**: Interactive seat selection with live availability updates
- **User Management**: Registration, login, profile management
- **Booking System**: Complete booking workflow with cart functionality
- **Admin Interface**: Powerful admin panel for managing events, venues, and bookings
- **Seat Categories**: Multiple pricing tiers (VIP, Premium, General, etc.)
- **Responsive Design**: Mobile-friendly Bootstrap interface

## Technology Stack

- **Backend**: Django 5.2.8
- **Database**: SQLite (development)
- **Frontend**: Bootstrap 5, jQuery
- **Icons**: Font Awesome 6

## Installation

1. Create and activate virtual environment:
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # On Windows PowerShell
```

2. Install dependencies:
```bash
pip install django pillow
```

3. Run migrations:
```bash
cd eventman
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Create media and static directories:
```bash
mkdir media
mkdir media\events
mkdir media\venues
mkdir media\profiles
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Access the application:
- Main site: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

## Usage

### For Users
1. Register an account or login
2. Browse events by category or search
3. View event details and seat availability
4. Select seats interactively
5. Complete booking through secure checkout
6. View and manage your bookings

### For Administrators
1. Login to admin panel
2. Add venues with capacity details
3. Create event categories
4. Add events with seat categories
5. Create individual seats for each category
6. Monitor bookings and payments

## Project Structure

```
eventman/
├── accounts/          # User authentication and profiles
├── events/           # Event management
├── bookings/         # Booking and ticket management
├── templates/        # HTML templates
├── static/          # CSS, JavaScript, images
├── media/           # User-uploaded files
└── eventman/        # Project settings
```

## Models

### Events App
- **Category**: Event categories (Music, Sports, Theater, etc.)
- **Venue**: Physical locations for events
- **Event**: Main event model with date, pricing, availability
- **SeatCategory**: Pricing tiers within an event
- **Seat**: Individual seats with status tracking

### Bookings App
- **Booking**: Main booking record
- **Ticket**: Individual tickets linked to seats
- **Payment**: Payment transaction records
- **Cart**: Temporary cart for seat selection
- **CartItem**: Individual cart items

### Accounts App
- **UserProfile**: Extended user information

## Key Features Implementation

### Real-Time Seat Availability
- AJAX endpoint checks seat status every 30 seconds
- Seat reservation during cart process (15-minute hold)
- Automatic release of expired reservations

### Booking Workflow
1. User selects seats on interactive seat map
2. Seats are temporarily reserved and added to cart
3. Cart expires after 15 minutes
4. User completes checkout with contact information
5. Payment is processed (simulated in development)
6. Booking is confirmed and seats are marked as booked

## Contact Information

- **Phone**: 9389761563
- **Email**: techslave19@gmail.com
- **Copyright**: © 2025 Shobhit Pandey

## Future Enhancements

- Payment gateway integration (Razorpay, Stripe)
- Email notifications for bookings
- QR code generation for tickets
- Event recommendations based on user preferences
- Social media integration
- Advanced analytics dashboard
- Mobile app

## License

© 2025 Shobhit Pandey. All rights reserved.

## Support

For support or queries, contact:
- Email: techslave19@gmail.com
- Phone: 9389761563
