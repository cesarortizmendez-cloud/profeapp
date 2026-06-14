import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from decimal import Decimal

from apps.courses.models import Course, Enrollment
from apps.accounts.models import User
from .models import GradeColumn, Grade, GradeReport
from .services import (
    calculate_weighted_average,
    recalculate_course_reports,
    export_grades_to_excel,
    import_students_from_excel,
    get_course_statistics,
)


def professor_required(view_func):
    """Decorador: solo profesores pueden acceder."""
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_professor:
            messages.error(request, 'Acceso restringido a profesores.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def gradebook_view(request, course_id):
    """
    Vista principal del libro de notas.
    Profesores ven todo, alumnos solo sus notas.
    """
    course = get_object_or_404(Course, pk=course_id)

    if request.user.is_professor:
        if course.professor != request.user:
            messages.error(request, 'No tienes acceso a este curso.')
            return redirect('dashboard:home')
        return _professor_gradebook(request, course)
    else:
        return _student_gradebook(request, course)


def _professor_gradebook(request, course):
    """Libro de notas para el profesor."""
    columns = GradeColumn.objects.filter(course=course).order_by('order', 'created_at')
    enrollments = Enrollment.objects.filter(
        course=course, is_active=True
    ).select_related('student').order_by('student__last_name', 'student__first_name')

    # Construir matriz de notas
    grade_matrix = []
    for enrollment in enrollments:
        student = enrollment.student
        average, detail = calculate_weighted_average(student, course)
        student_grades = {}
        for item in detail:
            student_grades[item['column'].id] = item

        report = GradeReport.objects.filter(student=student, course=course).first()
        grade_matrix.append({
            'student': student,
            'grades': student_grades,
            'average': average,
            'is_passing': report.is_passing if report else None,
        })

    stats = get_course_statistics(course)
    total_weight = sum(col.weight for col in columns)

    context = {
        'course': course,
        'columns': columns,
        'grade_matrix': grade_matrix,
        'stats': stats,
        'total_weight': total_weight,
        'weight_ok': abs(float(total_weight) - 100) < 0.01 if columns else False,
    }
    return render(request, 'grades/professor_gradebook.html', context)


def _student_gradebook(request, course):
    """Libro de notas para el alumno."""
    enrollment = get_object_or_404(Enrollment, course=course, student=request.user, is_active=True)
    columns = GradeColumn.objects.filter(course=course, is_published=True).order_by('order', 'created_at')
    average, detail = calculate_weighted_average(request.user, course)

    context = {
        'course': course,
        'detail': detail,
        'average': average,
        'is_passing': average >= Decimal('4.0') if average else None,
        'enrollment': enrollment,
    }
    return render(request, 'grades/student_gradebook.html', context)


@professor_required
def grade_column_create(request, course_id):
    """Crear una nueva columna de nota."""
    course = get_object_or_404(Course, pk=course_id, professor=request.user)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        weight = request.POST.get('weight', '0')
        grade_type = request.POST.get('grade_type', 'exam')
        date = request.POST.get('date') or None
        description = request.POST.get('description', '')

        if not name:
            messages.error(request, 'El nombre es requerido.')
        else:
            try:
                last_order = GradeColumn.objects.filter(course=course).count()
                GradeColumn.objects.create(
                    course=course,
                    name=name,
                    weight=Decimal(weight),
                    grade_type=grade_type,
                    date=date,
                    description=description,
                    order=last_order,
                )
                messages.success(request, f'Columna "{name}" creada.')
                recalculate_course_reports(course)
            except Exception as e:
                messages.error(request, f'Error al crear columna: {e}')

    return redirect('grades:gradebook', course_id=course_id)


@professor_required
def grade_column_toggle_publish(request, column_id):
    """Publicar/ocultar una columna de nota."""
    column = get_object_or_404(GradeColumn, pk=column_id, course__professor=request.user)
    column.is_published = not column.is_published
    column.save(update_fields=['is_published'])
    state = 'publicada' if column.is_published else 'ocultada'
    messages.success(request, f'Columna "{column.name}" {state}.')
    return redirect('grades:gradebook', course_id=column.course_id)


@professor_required
def grade_column_delete(request, column_id):
    """Eliminar una columna de nota."""
    column = get_object_or_404(GradeColumn, pk=column_id, course__professor=request.user)
    course_id = column.course_id
    name = column.name
    column.delete()
    recalculate_course_reports(Course.objects.get(pk=course_id))
    messages.success(request, f'Columna "{name}" eliminada.')
    return redirect('grades:gradebook', course_id=course_id)


@professor_required
@require_POST
def save_grade(request):
    """Guardar una nota individual (AJAX)."""
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        column_id = data.get('column_id')
        score_raw = data.get('score', '').strip()
        is_absent = data.get('is_absent', False)
        comment = data.get('comment', '').strip()

        column = get_object_or_404(GradeColumn, pk=column_id, course__professor=request.user)
        student = get_object_or_404(User, pk=student_id, role='student')

        score = None
        if score_raw:
            score = Decimal(score_raw.replace(',', '.'))
            if not (Decimal('1.0') <= score <= column.max_score):
                return JsonResponse({'ok': False, 'error': f'Nota fuera de rango (1.0 - {column.max_score})'})

        with transaction.atomic():
            grade, _ = Grade.objects.update_or_create(
                student=student,
                column=column,
                defaults={'score': score, 'is_absent': is_absent, 'comment': comment},
            )
            update_report = calculate_weighted_average(student, column.course)
            from .services import update_grade_report
            report = update_grade_report(student, column.course)

        return JsonResponse({
            'ok': True,
            'average': str(report.weighted_average) if report.weighted_average else None,
            'is_passing': report.is_passing,
        })
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@professor_required
def export_excel(request, course_id):
    """Exportar notas del curso a Excel."""
    course = get_object_or_404(Course, pk=course_id, professor=request.user)
    output = export_grades_to_excel(course)
    filename = f'notas_{course.name.replace(" ", "_")}_{course.year}.xlsx'
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@professor_required
def import_students(request, course_id):
    """Importar alumnos desde Excel."""
    course = get_object_or_404(Course, pk=course_id, professor=request.user)

    if request.method == 'POST' and request.FILES.get('excel_file'):
        file = request.FILES['excel_file']
        created, updated, errors = import_students_from_excel(file, course, request.user)

        if created:
            messages.success(request, f'{len(created)} alumno(s) creado(s): {", ".join(created[:5])}{"..." if len(created) > 5 else ""}')
        if updated:
            messages.info(request, f'{len(updated)} alumno(s) actualizado(s).')
        if errors:
            for err in errors[:5]:
                messages.error(request, err)
    else:
        messages.error(request, 'Selecciona un archivo Excel.')

    return redirect('grades:gradebook', course_id=course_id)
