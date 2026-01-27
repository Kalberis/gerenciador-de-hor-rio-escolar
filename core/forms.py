from django import forms
from .models import ConfiguracaoProfessor, ConfiguracaoTurma, DisponibilidadeProfessor, AtividadeExtra, RestricaoHorario

class ConfiguracaoProfessorForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoProfessor
        fields = ['aulas_diarias_max', 'aulas_semanais_max', 'dias_trabalho_max', 'prioridade_minimizacao', 'unidade']
        widgets = {
            'aulas_diarias_max': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'aulas_semanais_max': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 60}),
            'dias_trabalho_max': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 6}),
            'prioridade_minimizacao': forms.Select(attrs={'class': 'form-control'}),
            'unidade': forms.Select(attrs={'class': 'form-control'}),
        }

class ConfiguracaoTurmaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoTurma
        fields = ['aulas_por_semana', 'aulas_por_dia_max', 'preferencias_dias', 'disposicao_aulas']
        widgets = {
            'aulas_por_semana': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 30}),
            'aulas_por_dia_max': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 6}),
            'preferencias_dias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ex: ["segunda", "quarta", "sexta"]'}),
            'disposicao_aulas': forms.Select(attrs={'class': 'form-control'}),
        }

class DisponibilidadeProfessorForm(forms.ModelForm):
    class Meta:
        model = DisponibilidadeProfessor
        fields = ['professor', 'dia_semana', 'horario_inicio', 'horario_fim', 'unidade']
        widgets = {
            'professor': forms.Select(attrs={'class': 'form-control'}),
            'dia_semana': forms.Select(attrs={'class': 'form-control'}),
            'horario_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'horario_fim': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'unidade': forms.Select(attrs={'class': 'form-control'}),
        }

class AtividadeExtraForm(forms.ModelForm):
    class Meta:
        model = AtividadeExtra
        fields = ['titulo', 'tipo', 'descricao', 'data', 'horario_inicio', 'horario_fim', 'professores', 'sala', 'unidade']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'horario_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'horario_fim': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'professores': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'sala': forms.TextInput(attrs={'class': 'form-control'}),
            'unidade': forms.Select(attrs={'class': 'form-control'}),
        }

class RestricaoHorarioForm(forms.ModelForm):
    class Meta:
        model = RestricaoHorario
        fields = ['professor', 'turma', 'tipo', 'dia_semana', 'horario_inicio', 'horario_fim', 'descricao', 'unidade']
        widgets = {
            'professor': forms.Select(attrs={'class': 'form-control'}),
            'turma': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'dia_semana': forms.Select(attrs={'class': 'form-control'}),
            'horario_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'horario_fim': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unidade': forms.Select(attrs={'class': 'form-control'}),
        }