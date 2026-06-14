from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent, name='sent'),
    path('<int:message_id>/', views.message_detail, name='detail'),
    path('compose/', views.compose, name='compose'),
    path('<int:message_id>/reply/', views.reply, name='reply'),
    path('announcements/<int:course_id>/', views.announcements, name='announcements'),
    path('announcements/delete/<int:announcement_id>/', views.announcement_delete, name='announcement_delete'),
]
