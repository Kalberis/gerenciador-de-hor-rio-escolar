from django.contrib.auth import get_user_model
from django.db import models
class Perfil(models.Model):
	PERFIS = [
		('admin', 'Administrador'),
		('professor', 'Professor'),
		('visitante', 'Visitante'),
	]
	user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
	tipo = models.CharField(max_length=20, choices=PERFIS)

	def __str__(self):
		return f"{self.user.username} ({self.get_tipo_display()})"

class Turma(models.Model):
	nome = models.CharField(max_length=100)
	ano = models.IntegerField()

	def __str__(self):
		return f"{self.nome} ({self.ano})"

class Professor(models.Model):
	nome = models.CharField(max_length=100)
	disciplina = models.CharField(max_length=100)

	def __str__(self):
		return self.nome

class Disciplina(models.Model):
	nome = models.CharField(max_length=100)

	def __str__(self):
		return self.nome

class Horario(models.Model):
	turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
	professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
	disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
	sala = models.CharField(max_length=50, null=True, blank=True)
	DIAS_SEMANA = [
		('Segunda', 'Segunda-feira'),
		('Terça', 'Terça-feira'),
		('Quarta', 'Quarta-feira'),
		('Quinta', 'Quinta-feira'),
		('Sexta', 'Sexta-feira'),
	]
	dia_semana = models.CharField(max_length=10, choices=DIAS_SEMANA)
	horario_inicio = models.TimeField()
	horario_fim = models.TimeField()

	def __str__(self):
		return f"{self.turma} - {self.disciplina} ({self.dia_semana} {self.horario_inicio}-{self.horario_fim})"
