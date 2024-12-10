from django.contrib import admin
from django.urls import path
from project_management import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('', views.home, name='home'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('users/manage/', views.manage_users, name='manage_users'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path("add_user/", views.add_user, name="add_user"),
    path("delete_user/<int:user_id>/", views.delete_user, name="delete_user"),
    path('projects', views.projects, name='projects'), 
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),  
    path('projects/create/', views.create_project, name='create_project'), 
    path('projects/edit/<int:project_id>/', views.edit_project, name='edit_project'),  
    path('projects/delete/<int:project_id>/', views.delete_project, name='delete_project'),
    path('project/<int:project_id>/task/<int:task_id>/assign/', views.assign_task, name='assign_task'),
    path('project/<int:project_id>/task/add/', views.add_task, name='add_task'),
    path('project/tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('tasks/<int:task_id>/details/', views.task_details, name='task_details'),
    path('tasks/<int:task_id>/edit/', views.task_edit, name='edit_task'),
    path('projects/<int:task_id>/comments/', views.comments, name='comments'),
    path('project/<int:task_id>/add_comment/', views.comments, name='add_comment'),
    path('logs/', views.logs, name='logs')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
