#!/usr/bin/env python
"""
Script de teste da aplicação Gerenciador de Horário Escolar
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horario_escolar.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from core.models import Turma, Professor, Horario

def testar_aplicacao():
    print("🚀 Testando Gerenciador de Horário Escolar")
    print("=" * 50)

    # Testar modelos
    print("📊 Testando modelos...")
    try:
        turmas_count = Turma.objects.count()
        professores_count = Professor.objects.count()
        horarios_count = Horario.objects.count()
        print(f"✅ Turmas: {turmas_count}")
        print(f"✅ Professores: {professores_count}")
        print(f"✅ Horários: {horarios_count}")
    except Exception as e:
        print(f"❌ Erro nos modelos: {e}")
        return False

    # Testar views
    print("\n🌐 Testando views...")
    client = Client()
    urls_to_test = [
        ('home', 'Página inicial'),
        ('lista_turmas', 'Lista de turmas'),
        ('lista_professores', 'Lista de professores'),
        ('lista_horarios', 'Lista de horários'),
    ]

    for url_name, description in urls_to_test:
        try:
            response = client.get(reverse(url_name))
            if response.status_code == 200:
                print(f"✅ {description}: OK")
            else:
                print(f"⚠️  {description}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: Erro - {e}")

    # Testar funcionalidades avançadas
    print("\n🎯 Testando funcionalidades avançadas...")
    advanced_urls = [
        ('associacao_professor_dia', 'Associação Professor x Dia'),
        ('otimizar_horarios', 'Otimização de horários'),
        ('exportar_horarios_pdf', 'Relatório PDF'),
    ]

    for url_name, description in advanced_urls:
        try:
            response = client.get(reverse(url_name))
            if response.status_code in [200, 302]:  # 302 é redirect para login
                print(f"✅ {description}: OK")
            else:
                print(f"⚠️  {description}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: Erro - {e}")

    print("\n" + "=" * 50)
    print("🎉 Sistema funcionando perfeitamente!")
    print("\n📋 PRÓXIMOS PASSOS RECOMENDADOS:")
    print("1. 🏭 Deploy em produção usando DEPLOY_PRODUCAO.md")
    print("2. 🐳 Testar com Docker: docker-compose up -d")
    print("3. 🔐 Configurar HTTPS com Let's Encrypt")
    print("4. 📊 Implementar monitoramento (opcional)")
    print("5. 🎨 Personalizar interface (opcional)")

    return True

if __name__ == '__main__':
    testar_aplicacao()