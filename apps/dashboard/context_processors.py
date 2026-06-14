def sidebar_context(request):
    """Inyecta cursos/matrículas en el sidebar para todos los templates."""
    if not request.user.is_authenticated:
        return {}

    if request.user.is_professor:
        from apps.courses.models import Course
        sidebar_courses = Course.objects.filter(
            professor=request.user, is_active=True
        ).order_by('-year', '-semester')
        return {'sidebar_courses': sidebar_courses}
    else:
        from apps.courses.models import Enrollment
        sidebar_enrollments = Enrollment.objects.filter(
            student=request.user, is_active=True
        ).select_related('course')
        return {'sidebar_enrollments': sidebar_enrollments}