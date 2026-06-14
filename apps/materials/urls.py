from django.urls import path
from . import views

app_name = 'materials'

urlpatterns = [
    path('course/<int:course_id>/', views.material_list, name='list'),
    path('course/<int:course_id>/upload/', views.material_upload, name='upload'),
    path('<int:material_id>/delete/', views.material_delete, name='delete'),
    path('<int:material_id>/toggle/', views.material_toggle_visibility, name='toggle'),
]
