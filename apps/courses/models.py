from django.db import models
from django.conf import settings


class University(models.Model):
    """Universidad o institución."""
    name = models.CharField(max_length=200, verbose_name='Nombre')
    short_name = models.CharField(max_length=50, blank=True, verbose_name='Nombre corto')
    logo = models.ImageField(upload_to='universities/', blank=True, null=True, verbose_name='Logo')

    class Meta:
        verbose_name = 'Universidad'
        verbose_name_plural = 'Universidades'
        ordering = ['name']

    def __str__(self):
        return self.short_name or self.name


class Course(models.Model):
    """Curso o asignatura que dicta el profesor."""
    SEMESTER_CHOICES = [
        (1, 'Primer Semestre'),
        (2, 'Segundo Semestre'),
        (3, 'Anual'),
        (4, 'Verano'),
    ]

    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_taught',
        limit_choices_to={'role': 'professor'},
        verbose_name='Profesor',
    )
    university = models.ForeignKey(
        University,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses',
        verbose_name='Universidad',
    )
    name = models.CharField(max_length=200, verbose_name='Nombre del curso')
    code = models.CharField(max_length=30, blank=True, verbose_name='Código')
    description = models.TextField(blank=True, verbose_name='Descripción')
    section = models.CharField(max_length=20, blank=True, verbose_name='Sección')
    year = models.PositiveIntegerField(verbose_name='Año')
    semester = models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES, verbose_name='Período')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    color = models.CharField(
        max_length=7,
        default='#4361ee',
        verbose_name='Color del curso',
        help_text='Color hexadecimal para identificar el curso',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['-year', '-semester', 'name']
        unique_together = ['professor', 'code', 'section', 'year', 'semester']

    def __str__(self):
        sec = f' - Sec. {self.section}' if self.section else ''
        return f'{self.name}{sec} ({self.year})'

    def get_student_count(self):
        return self.enrollments.filter(is_active=True).count()

    def get_period_display_short(self):
        periods = {1: '1S', 2: '2S', 3: 'Anual', 4: 'Verano'}
        return f'{periods.get(self.semester, "")} {self.year}'


class Enrollment(models.Model):
    """Matriculación de un alumno en un curso."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Curso')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'},
        verbose_name='Estudiante',
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        unique_together = ['course', 'student']
        ordering = ['student__last_name', 'student__first_name']

    def __str__(self):
        return f'{self.student.get_full_name()} → {self.course}'


class EvaluationDate(models.Model):
    """Fechas importantes: evaluaciones, entregas, etc."""
    TYPE_EXAM = 'exam'
    TYPE_QUIZ = 'quiz'
    TYPE_TASK = 'task'
    TYPE_PROJECT = 'project'
    TYPE_OTHER = 'other'
    TYPE_CHOICES = [
        (TYPE_EXAM, 'Examen / Prueba'),
        (TYPE_QUIZ, 'Control'),
        (TYPE_TASK, 'Tarea'),
        (TYPE_PROJECT, 'Proyecto'),
        (TYPE_OTHER, 'Otro'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='evaluation_dates', verbose_name='Curso')
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(blank=True, verbose_name='Descripción')
    event_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_EXAM, verbose_name='Tipo')
    date = models.DateField(verbose_name='Fecha')
    time = models.TimeField(null=True, blank=True, verbose_name='Hora')
    location = models.CharField(max_length=200, blank=True, verbose_name='Sala / Lugar')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Fecha de evaluación'
        verbose_name_plural = 'Fechas de evaluación'
        ordering = ['date', 'time']

    def __str__(self):
        return f'{self.title} - {self.date}'
