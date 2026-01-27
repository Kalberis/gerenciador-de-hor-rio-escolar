import io
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
# ...existing code...
def exportar_horarios_pdf(request):
	from reportlab.lib.pagesizes import A4, landscape
	from reportlab.lib import colors
	from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
	from reportlab.lib.styles import getSampleStyleSheet
	from .models import Turma, Professor, Horario
	import io

	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="horario_manha_fundamental.pdf"'
	buffer = io.BytesIO()
	doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=20)
	elements = []
	styles = getSampleStyleSheet()
	title = Paragraph("<b>HORÁRIO MANHÃ FUNDAMENTAL – 03 DE JUNHO 2025</b>", styles['Title'])
	elements.append(title)
	elements.append(Spacer(1, 18))

	# Buscar turmas e professores do banco de dados
	turmas = list(Turma.objects.all().order_by('nome')[:4])  # Máximo 4 turmas para caber na tabela
	professores = list(Professor.objects.all())

	# Criar cabeçalho com nomes das turmas reais
	header = ['HORA'] + [turma.nome for turma in turmas]

	# Horários fixos
	horarios_base = [
		'07:00–08:00',
		'08:00–09:00',
		'09:20–10:20',
		'10:20–11:20',
		'11:20–12:20',
		'12:20–13:20'
	]

	# Criar dados da tabela
	dias = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']
	data = [header]

	# Para cada dia da semana
	for dia in dias:
		# Buscar horários reais para este dia
		horarios_do_dia = Horario.objects.filter(dia_semana=dia).select_related('turma', 'professor').order_by('horario_inicio')

		# Criar mapa de horário -> dados
		horario_map = {}
		for horario in horarios_do_dia:
			chave = f"{horario.horario_inicio.strftime('%H:%M')}–{horario.horario_fim.strftime('%H:%M')}"
			if horario.turma in turmas:
				idx = turmas.index(horario.turma)
				if chave not in horario_map:
					horario_map[chave] = [''] * len(turmas)
				horario_map[chave][idx] = f"Matemática\n{horario.professor.nome}"

		# Para cada horário base
		for i, horario_str in enumerate(horarios_base):
			if i == 0:
				# Primeira linha do dia
				row = [dia]
			else:
				# Linhas subsequentes
				row = ['']

			# Adicionar dados das turmas
			for j in range(len(turmas)):
				if horario_str in horario_map and j < len(horario_map[horario_str]):
					row.append(horario_map[horario_str][j])
				else:
					# Dados de exemplo se não houver horário real
					disciplinas = ['Matemática', 'Português', 'História', 'Geografia', 'Ciências', 'Inglês']
					prof_nomes = [p.nome for p in professores] if professores else ['Prof. João', 'Profª. Ana', 'Prof. Carlos', 'Profª. Luiza', 'Profª. Paula', 'Prof. Marcos']
					row.append(f"{disciplinas[(i + j) % len(disciplinas)]}\n{prof_nomes[j % len(prof_nomes)]}")

			data.append(row)

	table = Table(data, colWidths=[35] + [90] * len(turmas))
	table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ffe5c2')),
		('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#b85c00')),
		('ALIGN', (0, 0), (-1, -1), 'CENTER'),
		('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
		('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
		('FONTSIZE', (0, 0), (-1, 0), 12),
		('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
		('FONTSIZE', (0, 1), (-1, -1), 10),
		('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#ffe5c2')),
		('TEXTCOLOR', (0, 1), (0, -1), colors.HexColor('#b85c00')),
		('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
		('FONTSIZE', (0, 1), (0, -1), 11),
		('GRID', (0, 0), (-1, -1), 1.2, colors.HexColor('#e0c9a6')),
		('BACKGROUND', (1, 1), (-1, -1), colors.HexColor('#fffdfa')),
		('TEXTCOLOR', (1, 1), (-1, -1), colors.HexColor('#b85c00')),
		('ROWHEIGHT', (0, 0), (-1, -1), 28),
	]))
	elements.append(table)
	doc.build(elements)
	pdf = buffer.getvalue()
	buffer.close()
	response.write(pdf)
	return response

def home(request):
    # Estatísticas para o dashboard
    total_turmas = Turma.objects.count()
    total_professores = Professor.objects.count()
    total_horarios = Horario.objects.count()
    
    # Horários por dia da semana
    horarios_por_dia = {}
    for dia in ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']:
        horarios_por_dia[dia] = Horario.objects.filter(dia_semana=dia).count()
    
    context = {
        'total_turmas': total_turmas,
        'total_professores': total_professores,
        'total_horarios': total_horarios,
        'horarios_por_dia': horarios_por_dia,
    }
    return render(request, 'core/home.html', context)
@login_required
def editar_turma(request, pk):
	turma = Turma.objects.get(pk=pk)
	if request.method == 'POST':
		form = TurmaForm(request.POST, instance=turma)
		if form.is_valid():
			form.save()
			messages.success(request, 'Turma editada com sucesso!')
			return redirect('lista_turmas')
	else:
		form = TurmaForm(instance=turma)
	return render(request, 'core/editar_turma.html', {'form': form, 'turma': turma})

@login_required
def excluir_turma(request, pk):
	turma = Turma.objects.get(pk=pk)
	if request.method == 'POST':
		turma.delete()
		messages.success(request, 'Turma excluída com sucesso!')
		return redirect('lista_turmas')
	return render(request, 'core/excluir_turma.html', {'turma': turma})

@login_required
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

@login_required
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

@login_required
def excluir_horario(request, pk):
	horario = Horario.objects.get(pk=pk)
	if request.method == 'POST':
		horario.delete()
		return redirect('lista_horarios')
	return render(request, 'core/excluir_horario.html', {'horario': horario})
from django.shortcuts import render, redirect
from django import forms
from .models import Turma, Professor, Horario

class TurmaForm(forms.ModelForm):
	class Meta:
		model = Turma
		fields = ['nome']

@login_required
def cadastrar_turma(request):
	if request.method == 'POST':
		form = TurmaForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Turma cadastrada com sucesso!')
			return redirect('lista_turmas')
	else:
		form = TurmaForm()
	return render(request, 'core/cadastrar_turma.html', {'form': form})

class ProfessorForm(forms.ModelForm):
	class Meta:
		model = Professor
		fields = ['nome']

@login_required
def cadastrar_professor(request):
	if request.method == 'POST':
		form = ProfessorForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Professor cadastrado com sucesso!')
			return redirect('lista_professores')
	else:
		form = ProfessorForm()
	return render(request, 'core/cadastrar_professor.html', {'form': form})

class HorarioForm(forms.ModelForm):
	class Meta:
		model = Horario
		fields = ['turma', 'professor', 'dia_semana', 'horario_inicio', 'horario_fim', 'sala']

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

@login_required
def cadastrar_horario(request):
	if request.method == 'POST':
		form = HorarioForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Horário cadastrado com sucesso!')
			return redirect('lista_horarios')
	else:
		form = HorarioForm()
	return render(request, 'core/cadastrar_horario.html', {'form': form})

@login_required
def lista_turmas(request):
    query = request.GET.get('q', '')
    turmas = Turma.objects.all().order_by('nome')
    
    if query:
        turmas = turmas.filter(nome__icontains=query)
    
    paginator = Paginator(turmas, 10)  # 10 itens por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/lista_turmas.html', {
        'page_obj': page_obj,
        'query': query
    })

@login_required
def lista_professores(request):
    query = request.GET.get('q', '')
    professores = Professor.objects.all().order_by('nome')
    
    if query:
        professores = professores.filter(nome__icontains=query)
    
    paginator = Paginator(professores, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/lista_professores.html', {
        'page_obj': page_obj,
        'query': query
    })

@login_required
def lista_horarios(request):
	from .models import Horario, Turma, Professor
	turmas = Turma.objects.all()
	professores = Professor.objects.all()

	turma_id = request.GET.get('turma')
	professor_id = request.GET.get('professor')
	dia_semana = request.GET.get('dia_semana')

	horarios = Horario.objects.select_related('turma', 'professor').all()
	if turma_id:
		horarios = horarios.filter(turma_id=turma_id)
	if professor_id:
		horarios = horarios.filter(professor_id=professor_id)
	if dia_semana:
		horarios = horarios.filter(dia_semana__iexact=dia_semana)

	horarios = horarios.order_by('dia_semana', 'horario_inicio')

	# Obter todos os horários únicos cadastrados (hora de início)
	horarios_unicos = sorted(set(h.horario_inicio.strftime('%H:%M') for h in horarios))
	dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
	
	paginator = Paginator(horarios, 15)  # 15 horários por página
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	
	return render(request, 'core/lista_horarios.html', {
		'page_obj': page_obj,
		'horarios_unicos': horarios_unicos,
		'dias_semana': dias_semana,
		'turmas': turmas,
		'professores': professores,
		'selected_turma': turma_id,
		'selected_professor': professor_id,
		'selected_dia_semana': dia_semana,
	})
