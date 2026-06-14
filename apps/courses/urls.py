from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('create/', views.course_create, name='create'),
    path('<int:course_id>/evaluation/add/', views.evaluation_date_create, name='evaluation_add'),
    path('evaluation/<int:date_id>/delete/', views.evaluation_date_delete, name='evaluation_delete'),
]
