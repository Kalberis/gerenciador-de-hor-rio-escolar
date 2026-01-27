from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError
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

	def __str__(self):
		return self.nome

class Professor(models.Model):
	nome = models.CharField(max_length=100)

	def __str__(self):
		return self.nome

class Horario(models.Model):
	turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
	professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
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

	def clean(self):
		if self.horario_inicio >= self.horario_fim:
			raise ValidationError('Horário de início deve ser anterior ao horário de fim.')
		
		# Verificar conflitos de horário para o mesmo professor
		conflitos_professor = Horario.objects.filter(
			professor=self.professor,
			dia_semana=self.dia_semana
		).exclude(pk=self.pk)
		
		for horario in conflitos_professor:
			if (self.horario_inicio < horario.horario_fim and self.horario_fim > horario.horario_inicio):
				raise ValidationError(f'Conflito de horário com aula da {horario.turma} ({horario.horario_inicio}-{horario.horario_fim}).')
		
		# Verificar conflitos de sala (se sala estiver definida)
		if self.sala:
			conflitos_sala = Horario.objects.filter(
				sala=self.sala,
				dia_semana=self.dia_semana
			).exclude(pk=self.pk)
			
			for horario in conflitos_sala:
				if (self.horario_inicio < horario.horario_fim and self.horario_fim > horario.horario_inicio):
					raise ValidationError(f'Sala {self.sala} já está ocupada por aula da {horario.turma} ({horario.horario_inicio}-{horario.horario_fim}).')
		
		# Verificar conflitos de turma
		conflitos_turma = Horario.objects.filter(
			turma=self.turma,
			dia_semana=self.dia_semana
		).exclude(pk=self.pk)
		
		for horario in conflitos_turma:
			if (self.horario_inicio < horario.horario_fim and self.horario_fim > horario.horario_inicio):
				raise ValidationError(f'A {self.turma} já tem aula com {horario.professor} ({horario.horario_inicio}-{horario.horario_fim}).')

	def __str__(self):
		return f"{self.turma} - {self.professor} ({self.dia_semana} {self.horario_inicio}-{self.horario_fim})"
