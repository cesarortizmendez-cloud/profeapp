from django.db import models
from django.conf import settings


class Material(models.Model):
    """Material de estudio compartido por el profesor."""
    TYPE_CHOICES = [
        ('document', 'Documento'),
        ('presentation', 'Presentación'),
        ('video', 'Video (enlace)'),
        ('link', 'Enlace web'),
        ('exercise', 'Ejercicio'),
        ('guide', 'Guía'),
        ('other', 'Otro'),
    ]

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='materials',
        verbose_name='Curso',
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='materials_uploaded',
        verbose_name='Subido por',
    )
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(blank=True, verbose_name='Descripción')
    material_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='document', verbose_name='Tipo')
    file = models.FileField(upload_to='materials/%Y/%m/', blank=True, null=True, verbose_name='Archivo')
    url = models.URLField(blank=True, verbose_name='Enlace externo')
    is_visible = models.BooleanField(default=True, verbose_name='Visible para alumnos')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materiales'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.course})'

    def get_icon(self):
        icons = {
            'document': 'bi-file-earmark-text',
            'presentation': 'bi-file-earmark-slides',
            'video': 'bi-play-circle',
            'link': 'bi-link-45deg',
            'exercise': 'bi-pencil-square',
            'guide': 'bi-journal-text',
            'other': 'bi-paperclip',
        }
        return icons.get(self.material_type, 'bi-paperclip')
