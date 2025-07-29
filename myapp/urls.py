# urls.py
from django.urls import path
from . import views
from .views import transcribe_and_parse_task

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    path('subjects/', views.subjects_view, name='subjects'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    path('subjects/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    path('subjects/delete/', views.delete_subject, name='delete_subject'),

    path('tasks/add/', views.add_task, name='add_task'),
    path('tasks/<int:task_id>/toggle/', views.toggle_task_completion, name='toggle_task'),
    path('edit-task/', views.edit_task, name='edit_task'),
    path('delete-task/', views.delete_task, name='delete_task'),

    path('calendar/', views.calendar_view, name='calendar'),
    path('planner/add/', views.add_planner_task, name='add_planner_task'),
    path('planner/edit/', views.edit_planner_task, name='edit_planner_task'),
    path('planner/delete/', views.delete_planner_task, name='delete_planner_task'),
    path('planner/toggle/<int:task_id>/', views.toggle_planner_task_completion, name='toggle_planner_task'),

    path('statistics/', views.statistics_view, name='statistics'),   

    path('transcribe/', transcribe_and_parse_task, name='transcribe_task'), 
    

]