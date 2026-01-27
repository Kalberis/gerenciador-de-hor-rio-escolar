from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Turma, Professor, Horario

class ModelTests(TestCase):
    def test_turma_str(self):
        turma = Turma.objects.create(nome="Turma A")
        self.assertEqual(str(turma), "Turma A")

    def test_professor_str(self):
        professor = Professor.objects.create(nome="João Silva")
        self.assertEqual(str(professor), "João Silva")

    def test_horario_str(self):
        turma = Turma.objects.create(nome="Turma A")
        professor = Professor.objects.create(nome="João Silva")
        horario = Horario.objects.create(
            turma=turma,
            professor=professor,
            dia_semana="Segunda",
            horario_inicio="08:00",
            horario_fim="09:00",
            sala="Sala 1"
        )
        expected = "Turma A - João Silva (Segunda 08:00-09:00)"
        self.assertEqual(str(horario), expected)

class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_lista_turmas_view(self):
        response = self.client.get(reverse('lista_turmas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/lista_turmas.html')

    def test_lista_professores_view(self):
        response = self.client.get(reverse('lista_professores'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/lista_professores.html')

    def test_lista_horarios_view(self):
        response = self.client.get(reverse('lista_horarios'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/lista_horarios.html')

    def test_login_required_redirect(self):
        self.client.logout()
        response = self.client.get(reverse('lista_turmas'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])
