from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from apps.courses.models import Course, Enrollment, EvaluationDate
from apps.messaging.models import Message, Announcement
from apps.grades.models import GradeReport
from datetime import date, timedelta


@login_required
def home(request):
    """Dashboard principal, diferenciado por rol."""
    if request.user.is_professor:
        return _professor_dashboard(request)
    return _student_dashboard(request)


def _professor_dashboard(request):
    courses = Course.objects.filter(
        professor=request.user, is_active=True
    ).order_by('-year', '-semester')

    # Próximas evaluaciones (próximos 30 días)
    upcoming = EvaluationDate.objects.filter(
        course__professor=request.user,
        date__gte=date.today(),
        date__lte=date.today() + timedelta(days=30),
    ).select_related('course').order_by('date')[:10]

    unread_count = Message.objects.filter(recipient=request.user, is_read=False).count()

    context = {
        'courses': courses,
        'upcoming_dates': upcoming,
        'unread_count': unread_count,
        'total_students': sum(c.get_student_count() for c in courses),
    }
    return render(request, 'dashboard/professor.html', context)


def _student_dashboard(request):
    enrollments = Enrollment.objects.filter(
        student=request.user, is_active=True
    ).select_related('course', 'course__professor', 'course__university')

    # Notas y promedios
    course_data = []
    for enrollment in enrollments:
        course = enrollment.course
        report = GradeReport.objects.filter(student=request.user, course=course).first()
        
        # Próximas evaluaciones de este curso
        upcoming = EvaluationDate.objects.filter(
            course=course,
            date__gte=date.today(),
        ).order_by('date')[:3]

        # Anuncios recientes
        recent_announcements = Announcement.objects.filter(course=course).order_by('-created_at')[:2]

        course_data.append({
            'enrollment': enrollment,
            'course': course,
            'report': report,
            'upcoming': upcoming,
            'announcements': recent_announcements,
        })

    unread_count = Message.objects.filter(recipient=request.user, is_read=False).count()

    context = {
        'course_data': course_data,
        'unread_count': unread_count,
    }
    return render(request, 'dashboard/student.html', context)


@login_required
def course_detail(request, course_id):
    """Vista de detalle de un curso."""
    course = get_object_or_404(Course, pk=course_id)

    if request.user.is_professor and course.professor != request.user:
        return redirect('dashboard:home')
    if request.user.is_student:
        get_object_or_404(Enrollment, course=course, student=request.user, is_active=True)

    # Alumnos (solo si es profesor)
    enrollments = None
    if request.user.is_professor:
        enrollments = course.enrollments.filter(is_active=True).select_related('student')

    evaluation_dates = EvaluationDate.objects.filter(course=course).order_by('date')
    announcements = course.announcements.all()[:5]

    context = {
        'course': course,
        'enrollments': enrollments,
        'evaluation_dates': evaluation_dates,
        'announcements': announcements,
    }
    return render(request, 'dashboard/course_detail.html', context)
