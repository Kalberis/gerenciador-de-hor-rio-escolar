import io
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
# ...existing code...
def home(request):
    # Estatísticas para o dashboard
    total_turmas = Turma.objects.count()
    total_professores = Professor.objects.count()
    total_horarios = Horario.objects.count()
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
def exportar_horarios_pdf_moderno(request):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from .models import Turma, Professor, Horario

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="horario_escolar_moderno.pdf"'

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
    elements = []

    styles = getSampleStyleSheet()

    # Título moderno
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica-Bold'
    )

    title = Paragraph("HORÁRIO ESCOLAR", title_style)
    elements.append(title)

    # Subtítulo
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=20,
        alignment=1,
        textColor=colors.HexColor('#7f8c8d')
    )

    from datetime import datetime
    data_atual = datetime.now().strftime("%d/%m/%Y")
    subtitle = Paragraph(f"Gerado em {data_atual}", subtitle_style)
    elements.append(subtitle)

    elements.append(Spacer(1, 20))

    # Buscar dados
    turmas = list(Turma.objects.all().order_by('nome'))
    professores = list(Professor.objects.all())

    if not turmas:
        # Mensagem se não houver turmas
        no_data_style = ParagraphStyle(
            'NoData',
            parent=styles['Normal'],
            fontSize=14,
            alignment=1,
            textColor=colors.HexColor('#95a5a6'),
            spaceAfter=20
        )
        no_data = Paragraph("Nenhuma turma cadastrada no sistema.", no_data_style)
        elements.append(no_data)
    else:
        # Criar tabela moderna
        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']

        # Cabeçalho da tabela
        header = ['Horário'] + [turma.nome for turma in turmas[:6]]  # Máximo 6 turmas para caber na página

        # Dados da tabela
        data = [header]

        # Horários disponíveis
        horarios_disponiveis = [
            '07:00 - 08:00',
            '08:00 - 09:00',
            '09:20 - 10:20',
            '10:20 - 11:20',
            '11:20 - 12:20',
            '12:20 - 13:20'
        ]

        for horario_str in horarios_disponiveis:
            row = [horario_str]

            for turma in turmas[:6]:
                # Buscar horário para esta turma neste horário
                horario = Horario.objects.filter(
                    turma=turma,
                    horario_inicio__hour=int(horario_str.split(' - ')[0].split(':')[0]),
                    horario_inicio__minute=int(horario_str.split(' - ')[0].split(':')[1])
                ).select_related('professor').first()

                if horario:
                    cell_content = f"{horario.professor.nome}"
                    row.append(cell_content)
                else:
                    row.append("")

            data.append(row)

        # Criar tabela com estilo moderno
        col_widths = [1.2*inch] + [1.0*inch] * len(turmas[:6])

        table = Table(data, colWidths=col_widths)

        # Estilo moderno da tabela
        table_style = TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),

            # Coluna de horário
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#ecf0f1')),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, -1), 9),
            ('TEXTCOLOR', (0, 1), (0, -1), colors.HexColor('#2c3e50')),

            # Células de dados
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 1), (-1, -1), 8),
            ('TEXTCOLOR', (1, 1), (-1, -1), colors.HexColor('#34495e')),

            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2980b9')),

            # Fundo alternado para linhas
            ('BACKGROUND', (1, 1), (-1, 1), colors.HexColor('#f8f9fa')),
            ('BACKGROUND', (1, 3), (-1, 3), colors.HexColor('#f8f9fa')),
            ('BACKGROUND', (1, 5), (-1, 5), colors.HexColor('#f8f9fa')),

            # Padding das células
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ])

        table.setStyle(table_style)
        elements.append(table)

        # Legenda
        elements.append(Spacer(1, 20))

        legend_style = ParagraphStyle(
            'Legend',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=0
        )

        legend = Paragraph(
            f"<b>Legenda:</b> Tabela mostra a distribuição de professores por turma e horário. "
            f"Total de turmas: {len(turmas)} | Total de professores: {len(professores)}",
            legend_style
        )
        elements.append(legend)

    # Construir PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
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

@login_required
def otimizar_horarios(request):
	from .models import Horario, Professor, Turma, DisponibilidadeProfessor, ConfiguracaoProfessor, ConfiguracaoTurma, RestricaoHorario
	from datetime import datetime, time
	import random

	if request.method == 'POST':
		# Limpar horários existentes
		Horario.objects.all().delete()

		# Buscar configurações
		professores = list(Professor.objects.all())
		turmas = list(Turma.objects.all())
		disponibilidades = list(DisponibilidadeProfessor.objects.all())
		config_professores = {cp.professor_id: cp for cp in ConfiguracaoProfessor.objects.all()}
		config_turmas = {ct.turma_id: ct for ct in ConfiguracaoTurma.objects.all()}

		# Dias da semana
		dias = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']

		# Horários disponíveis
		horarios_disponiveis = [
			(time(7, 0), time(8, 0)),
			(time(8, 0), time(9, 0)),
			(time(9, 20), time(10, 20)),
			(time(10, 20), time(11, 20)),
			(time(11, 20), time(12, 20)),
			(time(12, 20), time(13, 20)),
		]

		# Algoritmo de otimização básico
		horarios_criados = []
		problemas = []

		for turma in turmas:
			config_turma = config_turmas.get(turma.id)
			aulas_por_semana = config_turma.aulas_por_semana if config_turma else 5
			aulas_por_dia_max = config_turma.aulas_por_dia_max if config_turma else 1

			aulas_agendadas = 0
			dias_usados = set()

			# Tentar distribuir aulas
			for dia in dias:
				if aulas_agendadas >= aulas_por_semana:
					break

				aulas_no_dia = 0

				for horario_inicio, horario_fim in horarios_disponiveis:
					if aulas_agendadas >= aulas_por_semana or aulas_no_dia >= aulas_por_dia_max:
						break

					# Encontrar professor disponível
					professor_disponivel = None
					for prof in professores:
						# Verificar disponibilidade
						disponivel = any(
							d.dia_semana == dia and
							d.horario_inicio <= horario_inicio and
							d.horario_fim >= horario_fim
							for d in disponibilidades if d.professor_id == prof.id
						)

						if disponivel:
							# Verificar carga de trabalho
							config_prof = config_professores.get(prof.id)
							if config_prof:
								# Contar aulas já agendadas para este professor neste dia
								aulas_prof_dia = len([h for h in horarios_criados
													if h['professor_id'] == prof.id and h['dia_semana'] == dia])
								aulas_prof_semana = len([h for h in horarios_criados
														if h['professor_id'] == prof.id])

								if (aulas_prof_dia < config_prof.aulas_diarias_max and
									aulas_prof_semana < config_prof.aulas_semanais_max):
									professor_disponivel = prof
									break

					if professor_disponivel:
						# Verificar conflitos
						conflito = any(
							h['dia_semana'] == dia and
							h['horario_inicio'] == horario_inicio and
							(h['professor_id'] == professor_disponivel.id or h['sala'] == turma.sala)
							for h in horarios_criados
						)

						if not conflito:
							horarios_criados.append({
								'turma_id': turma.id,
								'professor_id': professor_disponivel.id,
								'dia_semana': dia,
								'horario_inicio': horario_inicio,
								'horario_fim': horario_fim,
								'sala': turma.sala,
							})
							aulas_agendadas += 1
							aulas_no_dia += 1
							dias_usados.add(dia)

		# Criar horários no banco de dados
		for h in horarios_criados:
			try:
				Horario.objects.create(
					turma_id=h['turma_id'],
					professor_id=h['professor_id'],
					dia_semana=h['dia_semana'],
					horario_inicio=h['horario_inicio'],
					horario_fim=h['horario_fim'],
					sala=h['sala'],
				)
			except Exception as e:
				problemas.append(f"Erro ao criar horário: {str(e)}")

		messages.success(request, f'Otimização concluída! {len(horarios_criados)} horários criados.')
		if problemas:
			for problema in problemas:
				messages.warning(request, problema)

		return redirect('lista_horarios')

	return render(request, 'core/otimizar_horarios.html', {
		'professores': Professor.objects.all(),
		'turmas': Turma.objects.all(),
	})

@login_required
def configuracoes_professor(request):
	from .models import ConfiguracaoProfessor, Professor
	from .forms import ConfiguracaoProfessorForm

	configuracoes = ConfiguracaoProfessor.objects.select_related('professor').all()
	return render(request, 'core/configuracoes_professor.html', {
		'configuracoes': configuracoes,
	})

@login_required
def editar_configuracao_professor(request, pk):
	from .models import ConfiguracaoProfessor
	from .forms import ConfiguracaoProfessorForm

	config = get_object_or_404(ConfiguracaoProfessor, pk=pk)
	if request.method == 'POST':
		form = ConfiguracaoProfessorForm(request.POST, instance=config)
		if form.is_valid():
			form.save()
			messages.success(request, 'Configuração atualizada com sucesso!')
			return redirect('configuracoes_professor')
	else:
		form = ConfiguracaoProfessorForm(instance=config)

	return render(request, 'core/editar_configuracao_professor.html', {
		'form': form,
		'config': config,
	})

@login_required
def configuracoes_turma(request):
	from .models import ConfiguracaoTurma, Turma

	configuracoes = ConfiguracaoTurma.objects.select_related('turma').all()
	return render(request, 'core/configuracoes_turma.html', {
		'configuracoes': configuracoes,
	})

@login_required
def editar_configuracao_turma(request, pk):
	from .models import ConfiguracaoTurma
	from .forms import ConfiguracaoTurmaForm

	config = get_object_or_404(ConfiguracaoTurma, pk=pk)
	if request.method == 'POST':
		form = ConfiguracaoTurmaForm(request.POST, instance=config)
		if form.is_valid():
			form.save()
			messages.success(request, 'Configuração atualizada com sucesso!')
			return redirect('configuracoes_turma')
	else:
		form = ConfiguracaoTurmaForm(instance=config)

	return render(request, 'core/editar_configuracao_turma.html', {
		'form': form,
		'config': config,
	})

@login_required
def lista_disponibilidades(request):
	from .models import DisponibilidadeProfessor
	from .forms import DisponibilidadeProfessorForm

	disponibilidades = DisponibilidadeProfessor.objects.select_related('professor').all()
	return render(request, 'core/lista_disponibilidades.html', {
		'disponibilidades': disponibilidades,
	})

@login_required
def cadastrar_disponibilidade(request):
	from .models import DisponibilidadeProfessor
	from .forms import DisponibilidadeProfessorForm

	if request.method == 'POST':
		form = DisponibilidadeProfessorForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Disponibilidade cadastrada com sucesso!')
			return redirect('lista_disponibilidades')
	else:
		form = DisponibilidadeProfessorForm()

	return render(request, 'core/cadastrar_disponibilidade.html', {
		'form': form,
	})

@login_required
def editar_disponibilidade(request, pk):
	from .models import DisponibilidadeProfessor
	from .forms import DisponibilidadeProfessorForm

	disponibilidade = get_object_or_404(DisponibilidadeProfessor, pk=pk)
	if request.method == 'POST':
		form = DisponibilidadeProfessorForm(request.POST, instance=disponibilidade)
		if form.is_valid():
			form.save()
			messages.success(request, 'Disponibilidade atualizada com sucesso!')
			return redirect('lista_disponibilidades')
	else:
		form = DisponibilidadeProfessorForm(instance=disponibilidade)

	return render(request, 'core/editar_disponibilidade.html', {
		'form': form,
		'disponibilidade': disponibilidade,
	})

@login_required
def excluir_disponibilidade(request, pk):
	from .models import DisponibilidadeProfessor

	disponibilidade = get_object_or_404(DisponibilidadeProfessor, pk=pk)
	if request.method == 'POST':
		disponibilidade.delete()
		messages.success(request, 'Disponibilidade excluída com sucesso!')
		return redirect('lista_disponibilidades')

	return render(request, 'core/excluir_disponibilidade.html', {
		'disponibilidade': disponibilidade,
	})

@login_required
def lista_atividades_extras(request):
	from .models import AtividadeExtra

	atividades = AtividadeExtra.objects.select_related('unidade').prefetch_related('professores').all()
	return render(request, 'core/lista_atividades_extras.html', {
		'atividades': atividades,
	})

@login_required
def cadastrar_atividade_extra(request):
	from .models import AtividadeExtra
	from .forms import AtividadeExtraForm

	if request.method == 'POST':
		form = AtividadeExtraForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Atividade extra cadastrada com sucesso!')
			return redirect('lista_atividades_extras')
	else:
		form = AtividadeExtraForm()

	return render(request, 'core/cadastrar_atividade_extra.html', {
		'form': form,
	})

@login_required
def editar_atividade_extra(request, pk):
	from .models import AtividadeExtra
	from .forms import AtividadeExtraForm

	atividade = get_object_or_404(AtividadeExtra, pk=pk)
	if request.method == 'POST':
		form = AtividadeExtraForm(request.POST, instance=atividade)
		if form.is_valid():
			form.save()
			messages.success(request, 'Atividade extra atualizada com sucesso!')
			return redirect('lista_atividades_extras')
	else:
		form = AtividadeExtraForm(instance=atividade)

	return render(request, 'core/editar_atividade_extra.html', {
		'form': form,
		'atividade': atividade,
	})

@login_required
def excluir_atividade_extra(request, pk):
	from .models import AtividadeExtra

	atividade = get_object_or_404(AtividadeExtra, pk=pk)
	if request.method == 'POST':
		atividade.delete()
		messages.success(request, 'Atividade extra excluída com sucesso!')
		return redirect('lista_atividades_extras')

	return render(request, 'core/excluir_atividade_extra.html', {
		'atividade': atividade,
	})

@login_required
def lista_restricoes(request):
	from .models import RestricaoHorario

	restricoes = RestricaoHorario.objects.select_related('professor', 'turma', 'unidade').all()
	return render(request, 'core/lista_restricoes.html', {
		'restricoes': restricoes,
	})

@login_required
def cadastrar_restricao(request):
	from .models import RestricaoHorario
	from .forms import RestricaoHorarioForm

	if request.method == 'POST':
		form = RestricaoHorarioForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Restrição cadastrada com sucesso!')
			return redirect('lista_restricoes')
	else:
		form = RestricaoHorarioForm()

	return render(request, 'core/cadastrar_restricao.html', {
		'form': form,
	})

@login_required
def editar_restricao(request, pk):
	from .models import RestricaoHorario
	from .forms import RestricaoHorarioForm

	restricao = get_object_or_404(RestricaoHorario, pk=pk)
	if request.method == 'POST':
		form = RestricaoHorarioForm(request.POST, instance=restricao)
		if form.is_valid():
			form.save()
			messages.success(request, 'Restrição atualizada com sucesso!')
			return redirect('lista_restricoes')
	else:
		form = RestricaoHorarioForm(instance=restricao)

	return render(request, 'core/editar_restricao.html', {
		'form': form,
		'restricao': restricao,
	})

@login_required
def associacao_professor_dia(request):
	"""
	View que mostra a associação entre professores e dias da semana,
	incluindo disponibilidade e alocações atuais.
	"""
	from .models import Professor, DisponibilidadeProfessor, Horario

	professores = Professor.objects.all().order_by('nome')
	dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']

	# Criar matriz de associação
	associacao = {}

	for professor in professores:
		associacao[professor] = {}

		# Para cada dia da semana
		for dia in dias_semana:
			# Verificar disponibilidade
			disponibilidades = DisponibilidadeProfessor.objects.filter(
				professor=professor,
				dia_semana=dia
			)

			# Verificar alocações atuais
			alocacoes = Horario.objects.filter(
				professor=professor,
				dia_semana=dia
			).select_related('turma')

			associacao[professor][dia] = {
				'disponibilidades': list(disponibilidades),
				'alocacoes': list(alocacoes),
				'tem_disponibilidade': disponibilidades.exists(),
				'tem_alocacao': alocacoes.exists(),
			}

	context = {
		'professores': professores,
		'dias_semana': dias_semana,
		'associacao': associacao,
	}

	return render(request, 'core/associacao_professor_dia.html', context)

@login_required
def excluir_restricao(request, pk):
	from .models import RestricaoHorario

	restricao = get_object_or_404(RestricaoHorario, pk=pk)
	if request.method == 'POST':
		restricao.delete()
		messages.success(request, 'Restrição excluída com sucesso!')
		return redirect('lista_restricoes')

	return render(request, 'core/excluir_restricao.html', {
		'restricao': restricao,
	})
