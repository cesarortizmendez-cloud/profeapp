from django.urls import path
from . import views

app_name = 'grades'

urlpatterns = [
    path('course/<int:course_id>/', views.gradebook_view, name='gradebook'),
    path('course/<int:course_id>/column/create/', views.grade_column_create, name='column_create'),
    path('column/<int:column_id>/toggle/', views.grade_column_toggle_publish, name='column_toggle'),
    path('column/<int:column_id>/delete/', views.grade_column_delete, name='column_delete'),
    path('save/', views.save_grade, name='save_grade'),
    path('course/<int:course_id>/export/', views.export_excel, name='export_excel'),
    path('course/<int:course_id>/import/', views.import_students, name='import_students'),
]
