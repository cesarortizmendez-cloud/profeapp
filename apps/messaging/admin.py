from django.contrib import admin
from .models import Message, Announcement

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sender', 'recipient', 'is_read', 'sent_at']
    list_filter = ['is_read']

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'author', 'is_pinned', 'created_at']
