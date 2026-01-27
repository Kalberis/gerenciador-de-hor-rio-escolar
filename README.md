# 📚 Gerenciador de Horário Escolar

[![Django](https://img.shields.io/badge/Django-6.0.1-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Sistema web completo para gerenciamento de horários escolares, desenvolvido com Django. Inclui funcionalidades avançadas de otimização automática, controle de disponibilidade de professores e geração de relatórios em PDF.

## ✨ Funcionalidades

### 🎓 Gestão Básica
- ✅ **Turmas**: Cadastro, edição, exclusão e listagem
- ✅ **Professores**: Cadastro, edição, exclusão e listagem
- ✅ **Horários**: CRUD completo com validações de conflito
- ✅ **Disciplinas**: Vinculação com horários

### 🤖 Otimização Avançada
- ✅ **Algoritmo de Otimização**: Distribuição automática de horários
- ✅ **Disponibilidade de Professores**: Controle por dia da semana e período
- ✅ **Restrições de Horário**: Bloqueios e preferências personalizáveis
- ✅ **Configurações**: Regras específicas por professor e turma

### 📊 Relatórios e Visualização
- ✅ **Relatórios em PDF**: Horários formatados profissionalmente
- ✅ **Matriz Professor x Dia**: Visualização completa de associações
- ✅ **Atividades Extras**: Reuniões, formações e conselhos
- ✅ **Dashboard**: Estatísticas e métricas em tempo real

### 🔐 Segurança e Usuário
- ✅ **Autenticação**: Sistema de login/logout
- ✅ **Controle de Acesso**: Perfis de usuário configuráveis
- ✅ **Validações**: Prevenção de conflitos de horário
- ✅ **Auditoria**: Logs de todas as operações

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.11+
- PostgreSQL 15+
- Git

### Instalação Local (Desenvolvimento)

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/horario-escolar.git
   cd horario-escolar
   ```

2. **Configure o ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o banco de dados:**
   ```bash
   # Instale e configure PostgreSQL
   # Crie um banco de dados chamado 'horario_escolar'
   ```

5. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

6. **Execute as migrações:**
   ```bash
   python manage.py migrate
   ```

7. **Crie um superusuário:**
   ```bash
   python manage.py createsuperuser
   ```

8. **Inicie o servidor:**
   ```bash
   python manage.py runserver
   ```

9. **Acesse a aplicação:**
   - URL: http://127.0.0.1:8000
   - Admin: http://127.0.0.1:8000/admin

### 🐳 Instalação com Docker

1. **Clone e entre no diretório:**
   ```bash
   git clone https://github.com/seu-usuario/horario-escolar.git
   cd horario-escolar
   ```

2. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env
   ```

3. **Execute com Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Execute as migrações:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Crie um superusuário:**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## 🏭 Deploy em Produção

### Opção 1: Deploy Automatizado (Recomendado)

1. **Execute o script de deploy:**
   ```bash
   # Configure as variáveis no início do script deploy.sh
   ./deploy.sh
   ```

### Opção 2: Deploy Manual

Siga o guia completo em [`DEPLOY_PRODUCAO.md`](DEPLOY_PRODUCAO.md)

### Opção 3: Deploy com Docker

```bash
# Produção com Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Com SSL e Load Balancer
docker-compose -f docker-compose.prod.ssl.yml up -d
```

## 📁 Estrutura do Projeto

```
horario-escolar/
├── core/                          # App principal Django
│   ├── migrations/               # Migrações do banco
│   ├── templates/core/           # Templates HTML
│   ├── static/core/              # Arquivos estáticos
│   ├── models.py                 # Modelos de dados
│   ├── views.py                  # Lógica das views
│   ├── urls.py                   # URLs da aplicação
│   ├── forms.py                  # Formulários Django
│   └── admin.py                  # Configuração do admin
├── horario_escolar/              # Configurações do projeto
│   ├── settings.py              # Configurações Django
│   ├── urls.py                  # URLs principais
│   ├── wsgi.py                  # Configuração WSGI
│   └── asgi.py                  # Configuração ASGI
├── staticfiles/                  # Arquivos estáticos coletados
├── media/                        # Arquivos de mídia
├── requirements.txt              # Dependências Python
├── Dockerfile                    # Configuração Docker
├── docker-compose.yml           # Configuração Docker Compose
├── deploy.sh                     # Script de deploy automatizado
├── DEPLOY_PRODUCAO.md          # Guia completo de produção
└── README.md                    # Este arquivo
```

## 🛠️ Tecnologias Utilizadas

### Backend
- **Django 6.0.1**: Framework web Python
- **PostgreSQL**: Banco de dados relacional
- **Redis**: Cache e sessões
- **Gunicorn**: Servidor WSGI

### Frontend
- **Bootstrap 5**: Framework CSS responsivo
- **Font Awesome**: Ícones
- **JavaScript**: Interatividade

### Infraestrutura
- **Nginx**: Servidor web e proxy reverso
- **Docker**: Containerização
- **Let's Encrypt**: Certificados SSL gratuitos
- **Systemd**: Gerenciamento de serviços

## 🔧 Comandos Úteis

### Desenvolvimento
```bash
# Executar testes
python manage.py test

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic

# Criar superusuário
python manage.py createsuperuser

# Executar shell Django
python manage.py shell
```

### Produção
```bash
# Verificar status dos serviços
sudo systemctl status horario-escolar
sudo systemctl status nginx

# Ver logs
sudo journalctl -u horario-escolar -f
sudo tail -f /var/log/nginx/error.log

# Reiniciar serviços
sudo systemctl restart horario-escolar
sudo systemctl restart nginx

# Backup manual
sudo /usr/local/bin/backup-horario.sh
```

## 📊 API Endpoints

A aplicação inclui uma API REST básica para integração com outros sistemas:

- `GET /api/turmas/` - Lista turmas
- `GET /api/professores/` - Lista professores
- `GET /api/horarios/` - Lista horários
- `POST /api/horarios/otimizar/` - Otimizar horários

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

Para suporte técnico ou dúvidas:

- 📧 Email: suporte@horarioescolar.com
- 📱 WhatsApp: +55 11 99999-9999
- 📖 Documentação: [Wiki do Projeto](https://github.com/seu-usuario/horario-escolar/wiki)

## 🎯 Roadmap

### Próximas Funcionalidades
- [ ] **API REST completa** com autenticação OAuth2
- [ ] **Aplicativo Mobile** para professores e alunos
- [ ] **Integração com Google Calendar**
- [ ] **Sistema de notificações por email/SMS**
- [ ] **Relatórios avançados** com gráficos interativos
- [ ] **Backup na nuvem** (AWS S3, Google Cloud)
- [ ] **Multi-tenant** para múltiplas instituições
- [ ] **Integração com sistemas acadêmicos** (Moodle, etc.)

### Melhorias Planejadas
- [ ] **Interface responsiva** aprimorada
- [ ] **Tema dark/light** automático
- [ ] **PWA** (Progressive Web App)
- [ ] **Cache inteligente** com Redis
- [ ] **Monitoramento em tempo real** com Grafana
- [ ] **Testes automatizados** completos (95%+ cobertura)

---

## 📈 Status do Projeto

✅ **Funcionalidades Core**: 100% implementadas
✅ **Interface Web**: Completa e responsiva
✅ **Otimização**: Algoritmo funcional
✅ **Produção**: Scripts de deploy prontos
🔄 **Testes**: Em desenvolvimento
🔄 **Documentação**: Em desenvolvimento

**Última atualização**: Janeiro 2026
**Versão**: 1.0.0