from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'email', 'role', 'rut', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'rut']
    ordering = ['last_name', 'first_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('role', 'rut', 'phone', 'avatar', 'bio', 'must_change_password')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('first_name', 'last_name', 'email', 'role', 'rut', 'phone')
        }),
    )
