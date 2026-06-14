from django.contrib import admin
from .models import GradeColumn, Grade, GradeReport

@admin.register(GradeColumn)
class GradeColumnAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'weight', 'is_published', 'date']
    list_filter = ['is_published', 'grade_type']

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'column', 'score', 'is_absent', 'updated_at']
    list_filter = ['is_absent', 'column__course']
    search_fields = ['student__last_name', 'student__first_name']

@admin.register(GradeReport)
class GradeReportAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'weighted_average', 'is_passing', 'updated_at']
    list_filter = ['is_passing']
