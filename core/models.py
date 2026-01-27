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

class Unidade(models.Model):
	nome = models.CharField(max_length=100)
	endereco = models.TextField(blank=True)

	def __str__(self):
		return self.nome

class Periodo(models.Model):
	nome = models.CharField(max_length=50)  # Ex: "Manhã", "Tarde", "Noite"
	horario_inicio = models.TimeField()
	horario_fim = models.TimeField()
	unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return f"{self.nome} ({self.horario_inicio}-{self.horario_fim})"

class DisponibilidadeProfessor(models.Model):
	professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
	dia_semana = models.CharField(max_length=10, choices=Horario.DIAS_SEMANA)
	horario_inicio = models.TimeField()
	horario_fim = models.TimeField()
	unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return f"{self.professor} - {self.dia_semana} ({self.horario_inicio}-{self.horario_fim})"

class ConfiguracaoTurma(models.Model):
	turma = models.OneToOneField(Turma, on_delete=models.CASCADE)
	aulas_por_semana = models.PositiveIntegerField(default=5)
	aulas_por_dia_max = models.PositiveIntegerField(default=1)
	preferencias_dias = models.JSONField(default=list, blank=True)  # Lista de dias preferidos
	disposicao_aulas = models.CharField(max_length=20, choices=[
		('separadas', 'Aulas Separadas'),
		('duplicadas', 'Aulas Duplicadas'),
		('uma_por_dia', 'Uma Aula por Dia'),
		('concentradas', 'Aulas Concentradass'),
	], default='separadas')

	def __str__(self):
		return f"Configuração {self.turma}"

class ConfiguracaoProfessor(models.Model):
	professor = models.OneToOneField(Professor, on_delete=models.CASCADE)
	aulas_diarias_max = models.PositiveIntegerField(default=6)
	aulas_semanais_max = models.PositiveIntegerField(default=30)
	dias_trabalho_max = models.PositiveIntegerField(default=5)
	prioridade_minimizacao = models.CharField(max_length=20, choices=[
		('dias_trabalho', 'Minimizar Dias de Trabalho'),
		('vagas', 'Minimizar Vagas'),
		('equilibrado', 'Equilibrado'),
	], default='equilibrado')
	unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return f"Configuração {self.professor}"

class AtividadeExtra(models.Model):
	TIPOS_ATIVIDADE = [
		('reuniao', 'Reunião'),
		('formacao', 'Formação'),
		('conselho', 'Conselho de Classe'),
		('outro', 'Outro'),
	]

	titulo = models.CharField(max_length=200)
	tipo = models.CharField(max_length=20, choices=TIPOS_ATIVIDADE, default='reuniao')
	descricao = models.TextField(blank=True)
	data = models.DateField()
	horario_inicio = models.TimeField()
	horario_fim = models.TimeField()
	professores = models.ManyToManyField(Professor, blank=True)
	sala = models.CharField(max_length=50, blank=True)
	unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return f"{self.titulo} ({self.data})"

class RestricaoHorario(models.Model):
	TIPOS_RESTRICAO = [
		('bloqueio', 'Bloqueio de Horário'),
		('preferencia', 'Preferência de Horário'),
		('simultaneo', 'Aulas Simultâneas'),
		('local', 'Restrição de Local'),
	]

	professor = models.ForeignKey(Professor, on_delete=models.CASCADE, null=True, blank=True)
	turma = models.ForeignKey(Turma, on_delete=models.CASCADE, null=True, blank=True)
	tipo = models.CharField(max_length=20, choices=TIPOS_RESTRICAO)
	dia_semana = models.CharField(max_length=10, choices=Horario.DIAS_SEMANA, null=True, blank=True)
	horario_inicio = models.TimeField(null=True, blank=True)
	horario_fim = models.TimeField(null=True, blank=True)
	descricao = models.TextField()
	unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return f"{self.tipo} - {self.professor or self.turma}"
