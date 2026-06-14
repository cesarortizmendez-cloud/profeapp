from django.contrib import admin
from .models import University, Course, Enrollment, EvaluationDate

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'section', 'professor', 'year', 'semester', 'is_active']
    list_filter = ['is_active', 'year', 'semester']
    search_fields = ['name', 'code', 'professor__last_name']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'is_active']
    list_filter = ['is_active']

@admin.register(EvaluationDate)
class EvaluationDateAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'event_type', 'date']
    ordering = ['date']
