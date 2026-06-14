"""
Comando para inicializar ProfeApp con datos de ejemplo.
Uso: python manage.py setup_demo
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.courses.models import University, Course, Enrollment

User = get_user_model()

class Command(BaseCommand):
    help = 'Configura ProfeApp con datos de demostracion'

    def handle(self, *args, **options):
        self.stdout.write('\n Iniciando configuracion de ProfeApp...\n')

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin', email='admin@profeapp.cl', password='Admin1234!',
                first_name='Administrador', last_name='Sistema',
                role='professor', must_change_password=False,
            )
            self.stdout.write(self.style.SUCCESS('Superusuario creado: admin / Admin1234!'))

        prof, created = User.objects.get_or_create(
            username='profesor',
            defaults={
                'email': 'profesor@universidad.cl',
                'first_name': 'Carlos', 'last_name': 'Gonzalez',
                'role': 'professor', 'rut': '12345678-9',
                'must_change_password': False,
            }
        )
        if created:
            prof.set_password('Profe1234!')
            prof.save()
            self.stdout.write(self.style.SUCCESS('Profesor creado: profesor / Profe1234!'))

        uni1, _ = University.objects.get_or_create(
            name='Universidad de Chile', defaults={'short_name': 'UChile'})
        University.objects.get_or_create(
            name='Pontificia Universidad Catolica de Chile', defaults={'short_name': 'PUC'})
        self.stdout.write(self.style.SUCCESS('Universidades creadas'))

        course, created = Course.objects.get_or_create(
            professor=prof, name='Calculo I', year=2025, semester=1,
            defaults={'code': 'MAT101', 'section': 'A', 'university': uni1,
                      'description': 'Introduccion al calculo diferencial e integral.',
                      'color': '#4361ee'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Curso creado: {course}'))

        students_data = [
            ('11111111-1', 'Garcia', 'Maria', 'maria@alumno.cl'),
            ('22222222-2', 'Martinez', 'Juan', 'juan@alumno.cl'),
            ('33333333-3', 'Lopez', 'Ana', 'ana@alumno.cl'),
            ('44444444-4', 'Rodriguez', 'Pedro', 'pedro@alumno.cl'),
            ('55555555-5', 'Hernandez', 'Sofia', 'sofia@alumno.cl'),
        ]
        for rut, last, first, email in students_data:
            username = rut.replace('-', '').lower()
            student, c = User.objects.get_or_create(
                username=username,
                defaults={'rut': rut, 'last_name': last, 'first_name': first,
                          'email': email, 'role': 'student', 'must_change_password': False}
            )
            if c:
                student.set_password(rut)
                student.save()
            Enrollment.objects.get_or_create(course=course, student=student)

        self.stdout.write(self.style.SUCCESS(f'{len(students_data)} alumnos matriculados'))
        self.stdout.write(self.style.SUCCESS('\nProfeApp lista!'))
        self.stdout.write("""
Accesos de prueba:
  Admin    -> /admin/           admin / Admin1234!
  Profesor -> /accounts/login/  profesor / Profe1234!
  Alumno   -> /accounts/login/  111111111 / 11111111-1
""")
