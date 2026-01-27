# ...existing code...
def exportar_horarios_ics(request):
	from .models import Horario
	from icalendar import Calendar, Event
	import pytz
	cal = Calendar()
	cal.add('prodid', '-//Gerenciador Escolar//mxm.dk//')
	cal.add('version', '2.0')
	horarios = Horario.objects.select_related('turma', 'professor', 'disciplina').all()
	tz = pytz.timezone('America/Sao_Paulo')
	for h in horarios:
		event = Event()
		event.add('summary', f"{h.turma} - {h.disciplina}")
		event.add('description', f"Professor: {h.professor}")
		# Supondo que o campo dia_semana seja tipo string ('Segunda', etc.) e os horários sejam time
		# Para data, usar próxima semana como exemplo
		import datetime
		dias = {'Segunda': 0, 'Terça': 1, 'Quarta': 2, 'Quinta': 3, 'Sexta': 4}
		hoje = datetime.date.today()
		prox_dia = hoje + datetime.timedelta(days=(dias.get(h.dia_semana, 0) - hoje.weekday()) % 7)
		dtstart = datetime.datetime.combine(prox_dia, h.horario_inicio)
		dtend = datetime.datetime.combine(prox_dia, h.horario_fim)
		event.add('dtstart', tz.localize(dtstart))
		event.add('dtend', tz.localize(dtend))
		event.add('location', 'Escola')
		cal.add_component(event)
	response = HttpResponse(cal.to_ical(), content_type='text/calendar')
	response['Content-Disposition'] = 'attachment; filename="horarios_escola.ics"'
	return response
# ...existing code...
def exportar_horarios_pdf(request):
	from .models import Horario
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="horarios.pdf"'

	c = canvas.Canvas(response, pagesize=A4)
	width, height = A4

	horarios = Horario.objects.select_related('turma', 'professor', 'disciplina').all().order_by('turma', 'dia_semana', 'horario_inicio')
	data = [['Turma', 'Dia', 'Início', 'Fim', 'Professor', 'Disciplina']]
	for h in horarios:
		data.append([
			str(h.turma),
			h.dia_semana,
			h.horario_inicio.strftime('%H:%M'),
			h.horario_fim.strftime('%H:%M'),
			str(h.professor),
			str(h.disciplina)
		])

	table = Table(data, colWidths=[70, 50, 50, 50, 100, 100])
	style = TableStyle([
		('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
		('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
		('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Cabeçalho centralizado
		('ALIGN', (0, 1), (-1, -1), 'LEFT'),   # Dados alinhados à esquerda
		('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
		('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
		('FONTSIZE', (0, 0), (-1, 0), 11),
		('FONTSIZE', (0, 1), (-1, -1), 10),
		('BOTTOMPADDING', (0, 0), (-1, 0), 10),
		('TOPPADDING', (0, 0), (-1, 0), 8),
		('LEFTPADDING', (0, 0), (-1, -1), 6),
		('RIGHTPADDING', (0, 0), (-1, -1), 6),
		('GRID', (0, 0), (-1, -1), 1, colors.black),
	])
	table.setStyle(style)

	w, h = table.wrapOn(c, width - 40, height)
	table.drawOn(c, 20, height - h - 60)

	c.showPage()
	c.save()
	return response
import io
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

def exportar_horarios_excel(request):
    from .models import Horario
    horarios = Horario.objects.select_related('turma', 'professor', 'disciplina').all()
    data = []
    for h in horarios:
        data.append({
            'Turma': str(h.turma),
            'Disciplina': str(h.disciplina),
            'Professor': str(h.professor),
            'Dia': h.dia_semana,
            'Início': h.horario_inicio,
            'Fim': h.horario_fim,
        })
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Horários')
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=horarios.xlsx'
    return response
def home(request):
	return render(request, 'core/home.html')
def editar_turma(request, pk):
	turma = Turma.objects.get(pk=pk)
	if request.method == 'POST':
		form = TurmaForm(request.POST, instance=turma)
		if form.is_valid():
			form.save()
			return redirect('lista_turmas')
	else:
		form = TurmaForm(instance=turma)
	return render(request, 'core/editar_turma.html', {'form': form, 'turma': turma})

def excluir_turma(request, pk):
	turma = Turma.objects.get(pk=pk)
	if request.method == 'POST':
		turma.delete()
		return redirect('lista_turmas')
	return render(request, 'core/excluir_turma.html', {'turma': turma})

def editar_professor(request, pk):
	professor = Professor.objects.get(pk=pk)
	if request.method == 'POST':
		form = ProfessorForm(request.POST, instance=professor)
		if form.is_valid():
			form.save()
			return redirect('lista_professores')
	else:
		form = ProfessorForm(instance=professor)
	return render(request, 'core/editar_professor.html', {'form': form, 'professor': professor})

def excluir_professor(request, pk):
	professor = Professor.objects.get(pk=pk)
	if request.method == 'POST':
		professor.delete()
		return redirect('lista_professores')
	return render(request, 'core/excluir_professor.html', {'professor': professor})

def editar_disciplina(request, pk):
	disciplina = Disciplina.objects.get(pk=pk)
	if request.method == 'POST':
		form = DisciplinaForm(request.POST, instance=disciplina)
		if form.is_valid():
			form.save()
			return redirect('lista_disciplinas')
	else:
		form = DisciplinaForm(instance=disciplina)
	return render(request, 'core/editar_disciplina.html', {'form': form, 'disciplina': disciplina})

def excluir_disciplina(request, pk):
	disciplina = Disciplina.objects.get(pk=pk)
	if request.method == 'POST':
		disciplina.delete()
		return redirect('lista_disciplinas')
	return render(request, 'core/excluir_disciplina.html', {'disciplina': disciplina})

def editar_horario(request, pk):
	horario = Horario.objects.get(pk=pk)
	if request.method == 'POST':
		form = HorarioForm(request.POST, instance=horario)
		if form.is_valid():
			form.save()
			return redirect('lista_horarios')
	else:
		form = HorarioForm(instance=horario)
	return render(request, 'core/editar_horario.html', {'form': form, 'horario': horario})

def excluir_horario(request, pk):
	horario = Horario.objects.get(pk=pk)
	if request.method == 'POST':
		horario.delete()
		return redirect('lista_horarios')
	return render(request, 'core/excluir_horario.html', {'horario': horario})
from django.shortcuts import render, redirect
from django import forms
from .models import Turma, Professor, Disciplina, Horario

class TurmaForm(forms.ModelForm):
	class Meta:
		model = Turma
		fields = ['nome', 'ano']

def cadastrar_turma(request):
	if request.method == 'POST':
		form = TurmaForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('lista_turmas')
	else:
		form = TurmaForm()
	return render(request, 'core/cadastrar_turma.html', {'form': form})

class ProfessorForm(forms.ModelForm):
	class Meta:
		model = Professor
		fields = ['nome', 'disciplina']

def cadastrar_professor(request):
	if request.method == 'POST':
		form = ProfessorForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('lista_professores')
	else:
		form = ProfessorForm()
	return render(request, 'core/cadastrar_professor.html', {'form': form})

class DisciplinaForm(forms.ModelForm):
	class Meta:
		model = Disciplina
		fields = ['nome']

def cadastrar_disciplina(request):
	if request.method == 'POST':
		form = DisciplinaForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('lista_disciplinas')
	else:
		form = DisciplinaForm()
	return render(request, 'core/cadastrar_disciplina.html', {'form': form})

class HorarioForm(forms.ModelForm):
	class Meta:
		model = Horario
		fields = ['turma', 'professor', 'disciplina', 'dia_semana', 'horario_inicio', 'horario_fim', 'sala']

	def clean(self):
		cleaned_data = super().clean()
		turma = cleaned_data.get('turma')
		professor = cleaned_data.get('professor')
		dia_semana = cleaned_data.get('dia_semana')
		inicio = cleaned_data.get('horario_inicio')
		fim = cleaned_data.get('horario_fim')

		if turma and dia_semana and inicio and fim:
			conflito_turma = Horario.objects.filter(
				turma=turma,
				dia_semana=dia_semana,
				horario_inicio__lt=fim,
				horario_fim__gt=inicio
			)
			if self.instance.pk:
				conflito_turma = conflito_turma.exclude(pk=self.instance.pk)
			if conflito_turma.exists():
				raise forms.ValidationError('A turma já possui uma aula nesse horário.')

		if professor and dia_semana and inicio and fim:
			conflito_prof = Horario.objects.filter(
				professor=professor,
				dia_semana=dia_semana,
				horario_inicio__lt=fim,
				horario_fim__gt=inicio
			)
			if self.instance.pk:
				conflito_prof = conflito_prof.exclude(pk=self.instance.pk)
			if conflito_prof.exists():
				raise forms.ValidationError('O professor já está alocado nesse horário.')

		sala = cleaned_data.get('sala')

		if sala and dia_semana and inicio and fim:
			conflito_sala = Horario.objects.filter(
				sala=sala,
				dia_semana=dia_semana,
				horario_inicio__lt=fim,
				horario_fim__gt=inicio
			)
			if self.instance.pk:
				conflito_sala = conflito_sala.exclude(pk=self.instance.pk)
			if conflito_sala.exists():
				raise forms.ValidationError('A sala já está ocupada nesse horário.')

		return cleaned_data

def cadastrar_horario(request):
	if request.method == 'POST':
		form = HorarioForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('lista_horarios')
	else:
		form = HorarioForm()
	return render(request, 'core/cadastrar_horario.html', {'form': form})
from django.shortcuts import render
from .models import Turma, Professor, Disciplina, Horario

def lista_turmas(request):
	turmas = Turma.objects.all()
	return render(request, 'core/lista_turmas.html', {'turmas': turmas})

def lista_professores(request):
	professores = Professor.objects.all()
	return render(request, 'core/lista_professores.html', {'professores': professores})

def lista_disciplinas(request):
	disciplinas = Disciplina.objects.all()
	return render(request, 'core/lista_disciplinas.html', {'disciplinas': disciplinas})

def lista_horarios(request):
	from .models import Horario, Turma, Professor, Disciplina
	turmas = Turma.objects.all()
	professores = Professor.objects.all()
	disciplinas = Disciplina.objects.all()

	turma_id = request.GET.get('turma')
	professor_id = request.GET.get('professor')
	disciplina_id = request.GET.get('disciplina')
	dia_semana = request.GET.get('dia_semana')

	horarios = Horario.objects.select_related('turma', 'professor', 'disciplina').all()
	if turma_id:
		horarios = horarios.filter(turma_id=turma_id)
	if professor_id:
		horarios = horarios.filter(professor_id=professor_id)
	if disciplina_id:
		horarios = horarios.filter(disciplina_id=disciplina_id)
	if dia_semana:
		horarios = horarios.filter(dia_semana__iexact=dia_semana)

	# Obter todos os horários únicos cadastrados (hora de início)
	horarios_unicos = sorted(set(h.horario_inicio.strftime('%H:%M') for h in horarios))
	return render(request, 'core/lista_horarios.html', {
		'horarios': horarios,
		'horarios_unicos': horarios_unicos,
		'turmas': turmas,
		'professores': professores,
		'disciplinas': disciplinas,
		'selected_turma': turma_id,
		'selected_professor': professor_id,
		'selected_disciplina': disciplina_id,
		'selected_dia_semana': dia_semana,
	})
