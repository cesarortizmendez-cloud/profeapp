from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Course, University, EvaluationDate, Enrollment


@login_required
def course_create(request):
    if not request.user.is_professor:
        return redirect('dashboard:home')

    universities = University.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'El nombre del curso es requerido.')
            return render(request, 'courses/create.html', {'universities': universities})

        uni_id = request.POST.get('university') or None
        university = University.objects.filter(pk=uni_id).first() if uni_id else None

        course = Course.objects.create(
            professor=request.user,
            university=university,
            name=name,
            code=request.POST.get('code', ''),
            section=request.POST.get('section', ''),
            description=request.POST.get('description', ''),
            year=int(request.POST.get('year', 2025)),
            semester=int(request.POST.get('semester', 1)),
            color=request.POST.get('color', '#4361ee'),
        )
        messages.success(request, f'Curso "{name}" creado exitosamente.')
        return redirect('dashboard:course_detail', course_id=course.pk)

    context = {
        'universities': universities,
        'current_year': __import__('datetime').date.today().year,
    }
    return render(request, 'courses/create.html', context)


@login_required
def evaluation_date_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id, professor=request.user)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        date_val = request.POST.get('date', '')
        if title and date_val:
            EvaluationDate.objects.create(
                course=course,
                title=title,
                description=request.POST.get('description', ''),
                event_type=request.POST.get('event_type', 'exam'),
                date=date_val,
                time=request.POST.get('time') or None,
                location=request.POST.get('location', ''),
            )
            messages.success(request, f'Fecha "{title}" agregada.')
        else:
            messages.error(request, 'Título y fecha son requeridos.')

    return redirect('dashboard:course_detail', course_id=course_id)


@login_required
def evaluation_date_delete(request, date_id):
    ev = get_object_or_404(EvaluationDate, pk=date_id, course__professor=request.user)
    course_id = ev.course_id
    ev.delete()
    messages.success(request, 'Fecha eliminada.')
    return redirect('dashboard:course_detail', course_id=course_id)
