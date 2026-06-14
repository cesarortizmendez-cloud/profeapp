from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('courses/', include('apps.courses.urls')),
    path('grades/', include('apps.grades.urls')),
    path('materials/', include('apps.materials.urls')),
    path('messages/', include('apps.messaging.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Personalizar el admin
admin.site.site_header = 'ProfeApp - Administración'
admin.site.site_title = 'ProfeApp'
admin.site.index_title = 'Panel de administración'
