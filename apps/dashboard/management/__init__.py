"""
Comando para inicializar ProfeApp con datos de ejemplo.
Uso: python manage.py setup_demo

Crea:
- Superusuario admin
- Un profesor de ejemplo
- Dos universidades
- Un curso de ejemplo con alumnos
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.courses.models import University, Course, Enrollment

User = get_user_model()


class Command(BaseCommand):
    help = 'Configura ProfeApp con datos de demostración'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n🎓 Iniciando configuración de ProfeApp...\n'))

        # ── Superusuario ──
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@profeapp.cl',
                password='Admin1234!',
                first_name='Administrador',
                last_name='Sistema',
                role='professor',
                must_change_password=False,
            )
            self.stdout.write(self.style.SUCCESS('✅ Superusuario creado: admin / Admin1234!'))
        else:
            self.stdout.write('ℹ️  Superusuario admin ya existe.')

        # ── Profesor ──
        prof, created = User.objects.get_or_create(
            username='profesor',
            defaults={
                'email': 'profesor@universidad.cl',
                'first_name': 'Carlos',
                'last_name': 'González',
                'role': 'professor',
                'rut': '12345678-9',
                'must_change_password': False,
            }
        )
        if created:
            prof.set_password('Profe1234!')
            prof.save()
            self.stdout.write(self.style.SUCCESS('✅ Profesor creado: profesor / Profe1234!'))

        # ── Universidades ──
        uni1, _ = University.objects.get_or_create(
            name='Universidad de Chile',
            defaults={'short_name': 'UChile'}
        )
        uni2, _ = University.objects.get_or_create(
            name='Pontificia Universidad Católica de Chile',
            defaults={'short_name': 'PUC'}
        )
        self.stdout.write(self.style.SUCCESS('✅ Universidades creadas'))

        # ── Curso ──
        course, created = Course.objects.get_or_create(
            professor=prof,
            name='Cálculo I',
            year=2025,
            semester=1,
            defaults={
                'code': 'MAT101',
                'section': 'A',
                'university': uni1,
                'description': 'Introducción al cálculo diferencial e integral.',
                'color': '#4361ee',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Curso creado: {course}'))

        # ── Alumnos de ejemplo ──
        students_data = [
            ('11111111-1', 'García', 'María', 'maria.garcia@alumno.cl'),
            ('22222222-2', 'Martínez', 'Juan', 'juan.martinez@alumno.cl'),
            ('33333333-3', 'López', 'Ana', 'ana.lopez@alumno.cl'),
            ('44444444-4', 'Rodríguez', 'Pedro', 'pedro.rodriguez@alumno.cl'),
            ('55555555-5', 'Hernández', 'Sofía', 'sofia.hernandez@alumno.cl'),
        ]

        for rut, last, first, email in students_data:
            username = rut.replace('-', '').lower()
            student, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'rut': rut,
                    'last_name': last,
                    'first_name': first,
                    'email': email,
                    'role': 'student',
                    'must_change_password': False,
                }
            )
            if created:
                student.set_password(rut)
                student.save()
            Enrollment.objects.get_or_create(course=course, student=student)

        self.stdout.write(self.style.SUCCESS(f'✅ {len(students_data)} alumnos matriculados en {course}'))

        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('🚀 ProfeApp lista para usar!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'''
Accesos:
  Admin Django   → /admin/          usuario: admin     clave: Admin1234!
  Profesor       → /accounts/login/ usuario: profesor  clave: Profe1234!
  Alumno demo    → /accounts/login/ usuario: 111111111 clave: 11111111-1

URL local: http://127.0.0.1:8000/
''')
