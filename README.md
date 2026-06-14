# 🎓 ProfeApp

Sistema de gestión académica para profesores universitarios.  
Gestiona notas, materiales, fechas de evaluación y mensajería con tus alumnos — desde una sola plataforma.

base de datos postgres pgAdmin 4

profeapp_user

MiClave123



Accesos de prueba:
  Admin    -> /admin/           admin / Admin1234!
  Profesor -> /accounts/login/  profesor / Profe1234!
  Alumno   -> /accounts/login/  111111111 / 11111111-1

datos semilla:
          usuario           name            correo         Rol            RUT            Activo
	111111111	Maria Garcia	maria@alumno.cl	Estudiante	11111111-1	True
	profesor	Carlos Gonzalez	profesor@universidad.cl	Profesor	12345678-9	True
	555555555	Sofia Hernandez	sofia@alumno.cl	Estudiante	55555555-5	True
	333333333	Ana Lopez	ana@alumno.cl	Estudiante	33333333-3	True
	222222222	Juan Martinez	juan@alumno.cl	Estudiante	22222222-2	True
	444444444	Pedro Rodriguez	pedro@alumno.cl	Estudiante	44444444-4	True
	admin	Administrador Sistema	admin@profeapp.cl	Profesor	-





---

## ✨ Funcionalidades

| Módulo | Descripción |
|--------|-------------|
| 📊 **Libro de notas** | Notas con promedios ponderados automáticos, guardado AJAX en tiempo real |
| 📥 **Importar alumnos** | Carga masiva desde Excel (.xlsx) — RUT, nombre, apellido, email |
| 📤 **Exportar notas** | Excel profesional con estadísticas, colores y hoja de resumen |
| 📁 **Materiales** | Sube archivos o comparte enlaces externos por curso |
| 📅 **Fechas de evaluación** | Calendario de pruebas, tareas y proyectos visible por alumnos |
| 💬 **Mensajería** | Sistema de mensajes privados profesor ↔ alumno |
| 📢 **Anuncios** | Publicaciones del profesor para todos los alumnos del curso |
| 🔐 **Seguridad** | Cada alumno solo ve sus propias notas; contraseña inicial = RUT |
| 🏫 **Multi-universidad** | Un profesor puede tener cursos en distintas instituciones |

---

## 🚀 Instalación local (paso a paso)

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/profeapp.git
cd profeapp
```

### 2. Crear entorno virtual

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env con tu editor favorito
```

Mínimo indispensable en `.env`:
```
SECRET_KEY=una-clave-secreta-larga-y-aleatoria
DEBUG=True
DB_NAME=profeapp_db
DB_USER=profeapp_user
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Crear base de datos PostgreSQL

```bash
# En psql:
CREATE DATABASE profeapp_db;
CREATE USER profeapp_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE profeapp_db TO profeapp_user;
```

### 6. Ejecutar migraciones

```bash
python manage.py migrate
```

### 7. Cargar datos de demostración

```bash
python manage.py setup_demo
```

Esto crea:
- Superusuario: `admin` / `Admin1234!`
- Profesor demo: `profesor` / `Profe1234!`
- Alumno demo: `111111111` / `11111111-1`
- Un curso con 5 alumnos matriculados

### 8. Ejecutar servidor

```bash
python manage.py runserver
```

Abrir en el navegador: http://127.0.0.1:8000/

---

## 📋 Formato Excel para importar alumnos

El archivo debe tener estas columnas (el nombre puede variar, se detecta automáticamente):

| RUT | Apellidos | Nombre | Email |
|-----|-----------|--------|-------|
| 12345678-9 | García | María | maria@uni.cl |
| 98765432-1 | López | Juan | juan@uni.cl |

- **Contraseña inicial** de cada alumno = su RUT (ej: `12345678-9`)
- El alumno deberá cambiarla en su primer inicio de sesión
- Si el alumno ya existe, se actualizan sus datos

---

## ☁️ Deploy en Render.com (gratis)

### Requisitos previos
1. Cuenta en [render.com](https://render.com)
2. Repositorio en GitHub

### Pasos

1. **Subir a GitHub:**
```bash
git init
git add .
git commit -m "Initial commit - ProfeApp"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/profeapp.git
git push -u origin main
```

2. **En Render.com:**
   - New → **Blueprint** → conectar tu repositorio
   - Render leerá el archivo `render.yaml` automáticamente
   - Configurará la base de datos PostgreSQL y el web service

3. **Variables de entorno en Render** (se configuran automáticamente vía render.yaml):
   - `SECRET_KEY` — generada automáticamente
   - `DEBUG=False`
   - `DATABASE_URL` — del servicio PostgreSQL

4. **Después del deploy**, ejecutar en el Shell de Render:
```bash
python manage.py setup_demo
```

### Variables manuales si usas Railway u otro host:
```
SECRET_KEY=...
DEBUG=False
DATABASE_URL=postgres://user:pass@host:5432/dbname
ALLOWED_HOSTS=tu-dominio.onrender.com
```

---

## 🗂️ Estructura del proyecto

```
profeapp/
├── apps/
│   ├── accounts/       # Usuarios (profesor / alumno), autenticación
│   ├── courses/        # Cursos, matrículas, fechas de evaluación
│   ├── grades/         # Notas, columnas, promedios, export/import Excel
│   ├── materials/      # Archivos y enlaces por curso
│   ├── messaging/      # Mensajes privados y anuncios
│   └── dashboard/      # Vistas de inicio, gestión de cursos
├── templates/          # HTML por módulo
├── static/             # CSS, JS, imágenes propias
├── profeapp/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── .env.example
├── .gitignore
├── manage.py
├── Procfile
├── render.yaml
└── requirements.txt
```

---

## 🔑 Roles y permisos

| Acción | Profesor | Alumno |
|--------|----------|--------|
| Ver dashboard completo | ✅ | ✅ (solo sus cursos) |
| Crear/editar cursos | ✅ | ❌ |
| Ver libro de notas (todas) | ✅ | ❌ |
| Ver sus propias notas | — | ✅ (solo publicadas) |
| Importar alumnos | ✅ | ❌ |
| Exportar Excel | ✅ | ❌ |
| Subir materiales | ✅ | ❌ |
| Ver materiales visibles | ✅ | ✅ |
| Publicar anuncios | ✅ | ❌ |
| Enviar mensajes | ✅ (a sus alumnos) | ✅ (a sus profes) |

---

## 🛠️ Comandos útiles

```bash
# Crear migraciones tras modificar modelos
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recolectar estáticos para producción
python manage.py collectstatic

# Shell de Django
python manage.py shell
```

---

## 📌 Próximas mejoras sugeridas

- [ ] Gráficos de distribución de notas (Chart.js)
- [ ] Notificaciones por email al publicar notas/anuncios
- [ ] App móvil (PWA)
- [ ] Exportar lista de alumnos a PDF
- [ ] Adjuntar archivos en mensajes
- [ ] Historial de cambios en notas

---

Desarrollado con ❤️ usando Django 5 + PostgreSQL + Bootstrap 5
