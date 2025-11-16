from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


def register(request):
    """User registration"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        
        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('accounts:register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('accounts:register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('accounts:register')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        
        # Update profile with phone
        if phone:
            user.profile.phone = phone
            user.profile.save()
        
        login(request, user)
        messages.success(request, 'Registration successful!')
        return redirect('events:home')
    
    return render(request, 'accounts/register.html')


@login_required
def profile(request):
    """View user profile"""
    context = {
        'user': request.user,
        'profile': request.user.profile,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        user = request.user
        profile = user.profile
        
        # Update user info
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Update profile
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.state = request.POST.get('state', '')
        profile.zipcode = request.POST.get('zipcode', '')
        profile.country = request.POST.get('country', 'India')
        
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.receive_notifications = request.POST.get('receive_notifications') == 'on'
        profile.receive_promotional_emails = request.POST.get('receive_promotional_emails') == 'on'
        
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    context = {
        'user': request.user,
        'profile': request.user.profile,
    }
    return render(request, 'accounts/edit_profile.html', context)
