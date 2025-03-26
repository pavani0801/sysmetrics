from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dashboard_index'),
    path('processes/', views.processes, name='dashboard_processes'),
]