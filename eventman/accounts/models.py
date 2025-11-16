from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="India")
    zipcode = models.CharField(max_length=20, blank=True)
    
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Preferences
    receive_notifications = models.BooleanField(default=True)
    receive_promotional_emails = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_full_name(self):
        return self.user.get_full_name() or self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a profile when a new user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the profile whenever the user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
