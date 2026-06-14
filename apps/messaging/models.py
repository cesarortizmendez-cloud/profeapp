from django.db import models
from django.conf import settings


class Message(models.Model):
    """Mensaje entre profesor y alumno."""
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Remitente',
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='Destinatario',
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages',
        verbose_name='Curso relacionado',
    )
    subject = models.CharField(max_length=200, verbose_name='Asunto')
    body = models.TextField(verbose_name='Mensaje')
    is_read = models.BooleanField(default=False, verbose_name='Leído')
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='Respuesta a',
    )
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['-sent_at']

    def __str__(self):
        return f'{self.subject} ({self.sender} → {self.recipient})'


class Announcement(models.Model):
    """Anuncio del profesor para todos los alumnos de un curso."""
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='announcements',
        verbose_name='Curso',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='announcements',
        verbose_name='Autor',
    )
    title = models.CharField(max_length=200, verbose_name='Título')
    body = models.TextField(verbose_name='Contenido')
    is_pinned = models.BooleanField(default=False, verbose_name='Fijado')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Anuncio'
        verbose_name_plural = 'Anuncios'
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f'{self.title} ({self.course})'
