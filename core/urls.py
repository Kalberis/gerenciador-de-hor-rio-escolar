from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('horarios/exportar_pdf/', views.exportar_horarios_pdf, name='exportar_horarios_pdf'),
    path('', views.home, name='home'),
    path('turmas/', views.lista_turmas, name='lista_turmas'),
    path('turmas/cadastrar/', views.cadastrar_turma, name='cadastrar_turma'),
    path('turmas/<int:pk>/editar/', views.editar_turma, name='editar_turma'),
    path('turmas/<int:pk>/excluir/', views.excluir_turma, name='excluir_turma'),
    path('professores/', views.lista_professores, name='lista_professores'),
    path('professores/cadastrar/', views.cadastrar_professor, name='cadastrar_professor'),
    path('professores/<int:pk>/editar/', views.editar_professor, name='editar_professor'),
    path('professores/<int:pk>/excluir/', views.excluir_professor, name='excluir_professor'),
    path('horarios/', views.lista_horarios, name='lista_horarios'),
    path('horarios/cadastrar/', views.cadastrar_horario, name='cadastrar_horario'),
    path('horarios/<int:pk>/editar/', views.editar_horario, name='editar_horario'),
    path('horarios/<int:pk>/excluir/', views.excluir_horario, name='excluir_horario'),
]
