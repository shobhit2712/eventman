from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'state', 'receive_notifications')
    list_filter = ('receive_notifications', 'receive_promotional_emails', 'country', 'state')
    search_fields = ('user__username', 'user__email', 'phone', 'city')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('phone', 'address', 'city', 'state', 'country', 'zipcode')
        }),
        ('Profile', {
            'fields': ('profile_picture', 'date_of_birth')
        }),
        ('Preferences', {
            'fields': ('receive_notifications', 'receive_promotional_emails')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
