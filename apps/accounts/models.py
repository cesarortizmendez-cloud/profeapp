from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Usuario personalizado para ProfeApp."""
    
    ROLE_PROFESSOR = 'professor'
    ROLE_STUDENT = 'student'
    ROLE_CHOICES = [
        (ROLE_PROFESSOR, 'Profesor'),
        (ROLE_STUDENT, 'Estudiante'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_STUDENT,
        verbose_name='Rol',
    )
    rut = models.CharField(
        max_length=12,
        blank=True,
        verbose_name='RUT',
        help_text='Formato: 12345678-9',
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Foto de perfil',
    )
    bio = models.TextField(blank=True, verbose_name='Biografía')
    must_change_password = models.BooleanField(
        default=True,
        verbose_name='Debe cambiar contraseña',
        help_text='El alumno debe cambiar la contraseña en el primer login',
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.get_full_name()} ({self.get_role_display()})'

    @property
    def is_professor(self):
        return self.role == self.ROLE_PROFESSOR

    @property
    def is_student(self):
        return self.role == self.ROLE_STUDENT

    def get_full_name(self):
        full = f'{self.first_name} {self.last_name}'.strip()
        return full if full else self.username
