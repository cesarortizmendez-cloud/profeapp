from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.home, name='home_alt'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
]
