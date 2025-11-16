# EventMan - Quick Start Guide

## 🎉 Your Event Management Platform is Ready!

### What Has Been Built

A complete Django-based event management and ticket booking system with:

✅ **User Management**
- Registration and authentication
- User profiles with preferences
- Contact information management

✅ **Event Management**
- Event categories (Music, Sports, Theater, Comedy, Conference, Festival)
- Multiple venues across different cities
- Featured events showcase
- Event search and filtering

✅ **Booking System**
- Interactive seat selection with live seat map
- Multiple seat categories (VIP, Premium, General)
- Shopping cart with 15-minute reservation
- Secure checkout process
- Booking management and cancellation

✅ **Real-Time Features**
- Live seat availability updates
- Automatic cart expiration handling
- Real-time booking statistics

✅ **Admin Interface**
- Complete event and venue management
- Booking and ticket tracking
- User management

### Contact Information Configured

- **Phone**: 9389761563
- **Email**: techslave19@gmail.com
- **Copyright**: © 2025 Shobhit Pandey

### How to Run

1. **Navigate to project directory**:
   ```bash
   cd d:\dproj\eventman
   ```

2. **Activate virtual environment** (if not already):
   ```bash
   ..\.\venv\Scripts\Activate.ps1
   ```

3. **Start the server**:
   ```bash
   python manage.py runserver
   ```

4. **Access the application**:
   - Homepage: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

### Admin Credentials

- **Username**: admin
- **Password**: admin123

### Sample Data

The system includes sample data:
- 6 event categories
- 5 venues across Indian cities
- 3 upcoming events with seating arrangements
- Multiple seat categories per event

### Project Structure

```
eventman/
├── events/              # Event management app
├── bookings/            # Booking and ticketing
├── accounts/            # User authentication
├── templates/           # HTML templates
├── static/             # CSS, JavaScript
├── media/              # Uploaded files
├── db.sqlite3          # Database
├── manage.py           # Django management script
└── README.md           # Full documentation
```

### Key Features Implementation

1. **Event Discovery**
   - Browse all events at `/events/`
   - Search by keywords
   - Filter by category and city
   - Featured events on homepage

2. **Seat Selection**
   - Interactive seat map with color coding
   - Green: Available
   - Red: Booked
   - Yellow: Reserved
   - Blue: Selected
   - Real-time updates every 30 seconds

3. **Booking Flow**
   - Select seats → Add to cart → Checkout → Confirmation
   - Email confirmation (console in development)
   - Unique booking IDs with UUID
   - Downloadable booking details

4. **User Dashboard**
   - View all bookings
   - Booking details with tickets
   - Cancel bookings (releases seats)
   - Profile management

### Next Steps

1. **Add More Events**:
   - Go to admin panel
   - Create new events with seat categories
   - Upload event images

2. **Test Booking Flow**:
   - Register a new user
   - Browse events
   - Select seats and complete booking
   - View bookings in user dashboard

3. **Customize**:
   - Modify templates in `templates/`
   - Update styles in `static/css/style.css`
   - Add more categories or venues

### Future Enhancements

- Payment gateway integration (Razorpay/Stripe)
- Email notifications with SendGrid/AWS SES
- QR code tickets with ticket validation
- Event recommendations with ML
- Mobile responsive improvements
- PDF ticket generation
- Social media integration
- Analytics dashboard

### Troubleshooting

**If the server doesn't start**:
```bash
# Make sure you're in the right directory
cd d:\dproj\eventman

# Check if virtual environment is active
# You should see (.venv) in your prompt

# Run the server
python manage.py runserver
```

**If you see database errors**:
```bash
python manage.py migrate
```

**To create a new admin user**:
```bash
python manage.py createsuperuser
```

**To reset and recreate sample data**:
```bash
# Delete db.sqlite3
# Run migrations again
python manage.py migrate
python manage.py create_sample_data
```

### File Locations

- **Models**: `events/models.py`, `bookings/models.py`, `accounts/models.py`
- **Views**: `events/views.py`, `bookings/views.py`, `accounts/views.py`
- **URLs**: `eventman/urls.py`, `events/urls.py`, `bookings/urls.py`, `accounts/urls.py`
- **Templates**: `templates/` directory
- **Static Files**: `static/css/style.css`
- **Settings**: `eventman/settings.py`

### Support

For any issues or questions:
- Email: techslave19@gmail.com
- Phone: 9389761563

---

**Built with Django 5.2.8 | © 2025 Shobhit Pandey**
