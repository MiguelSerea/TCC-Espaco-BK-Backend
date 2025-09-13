from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    path('auth/check/', views.check_auth, name='check_auth'),
    
    # Tarefas
    path('tarefas/', views.tarefas_list, name='tarefas_list'),
    path('tarefas/<str:pk>/', views.tarefa_detail, name='tarefa_detail'),
    path('tarefas/<str:pk>/concluir/', views.marcar_tarefa_concluida, name='marcar_concluida'),
    
    # Clientes
    path('clientes/', views.clientes_list, name='clientes_list'),
]