from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView


urlpatterns = [
    path('', views.index, name='dashboard_index'),
    path('processes/', views.processes, name='dashboard_processes'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
]