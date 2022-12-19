from django.urls import path

from . import views

urlpatterns = [
    path('', views.get_index, name='index'),
    path('detail/<int:task_id>/', views.task_detail, name='detail'),
    path('create/', views.create_task, name='add_task'),
]