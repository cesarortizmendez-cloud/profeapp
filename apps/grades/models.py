from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class GradeColumn(models.Model):
    """Columna de nota (ej: Prueba 1, Tarea 1, Examen Final)."""
    GRADE_TYPE_CHOICES = [
        ('exam', 'Prueba / Examen'),
        ('quiz', 'Control'),
        ('task', 'Tarea'),
        ('project', 'Proyecto'),
        ('participation', 'Participación'),
        ('other', 'Otro'),
    ]

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='grade_columns',
        verbose_name='Curso',
    )
    name = models.CharField(max_length=100, verbose_name='Nombre')
    grade_type = models.CharField(max_length=20, choices=GRADE_TYPE_CHOICES, default='exam', verbose_name='Tipo')
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Ponderación (%)',
        help_text='Porcentaje de esta nota en la nota final (ej: 30 = 30%)',
    )
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal('7.0'),
        verbose_name='Nota máxima',
    )
    min_passing = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=Decimal('4.0'),
        verbose_name='Nota mínima de aprobación',
    )
    date = models.DateField(null=True, blank=True, verbose_name='Fecha de evaluación')
    description = models.TextField(blank=True, verbose_name='Descripción / Comentario')
    order = models.PositiveIntegerField(default=0, verbose_name='Orden')
    is_published = models.BooleanField(
        default=False,
        verbose_name='Publicada',
        help_text='Si está marcada, los alumnos pueden ver esta nota',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Columna de nota'
        verbose_name_plural = 'Columnas de notas'
        ordering = ['order', 'created_at']
        unique_together = ['course', 'name']

    def __str__(self):
        return f'{self.name} ({self.course})'

    def get_weight_as_fraction(self):
        """Retorna el peso como fracción (0.0 - 1.0)."""
        return float(self.weight) / 100


class Grade(models.Model):
    """Nota de un alumno en una columna."""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name='Estudiante',
    )
    column = models.ForeignKey(
        GradeColumn,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name='Columna',
    )
    score = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('7.0'))],
        verbose_name='Nota',
    )
    is_absent = models.BooleanField(default=False, verbose_name='Ausente')
    comment = models.TextField(blank=True, verbose_name='Comentario del profesor')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        unique_together = ['student', 'column']

    def __str__(self):
        score_str = str(self.score) if self.score is not None else 'S/N'
        return f'{self.student.get_full_name()} | {self.column.name}: {score_str}'

    def get_effective_score(self):
        """Retorna la nota efectiva (1.0 si está ausente y no hay nota)."""
        if self.is_absent and self.score is None:
            return Decimal('1.0')
        return self.score

    def is_passing(self):
        score = self.get_effective_score()
        if score is None:
            return None
        return score >= self.column.min_passing


class GradeReport(models.Model):
    """Reporte calculado del promedio ponderado de un alumno en un curso."""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='grade_reports',
        verbose_name='Estudiante',
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='grade_reports',
        verbose_name='Curso',
    )
    weighted_average = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='Promedio ponderado',
    )
    is_passing = models.BooleanField(null=True, blank=True, verbose_name='Aprobado')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reporte de notas'
        verbose_name_plural = 'Reportes de notas'
        unique_together = ['student', 'course']

    def __str__(self):
        avg = str(self.weighted_average) if self.weighted_average else 'Sin notas'
        return f'{self.student.get_full_name()} | {self.course}: {avg}'
