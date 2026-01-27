# Gerenciador de Horário Escolar - Guia de Produção

## 📋 Pré-requisitos para Produção

### 1. Servidor
- Ubuntu 20.04+ ou CentOS 7+
- Pelo menos 2GB RAM, 1GB para aplicação
- 20GB espaço em disco

### 2. Domínio
- Domínio registrado (ex: horarioescola.com)
- Configuração DNS apontando para o servidor

### 3. Certificado SSL
- Let's Encrypt (gratuito) ou certificado pago

## 🚀 Guia de Deploy

### Passo 1: Preparar o Servidor

```bash
# Atualizar o sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências básicas
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server

# Instalar Node.js para assets (opcional)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Passo 2: Configurar PostgreSQL

```bash
# Criar usuário e banco
sudo -u postgres psql
CREATE DATABASE horario_escolar;
CREATE USER horario_user WITH PASSWORD 'sua_senha_segura';
GRANT ALL PRIVILEGES ON DATABASE horario_escolar TO horario_user;
\q

# Configurar PostgreSQL para aceitar conexões locais
sudo nano /etc/postgresql/12/main/pg_hba.conf
# Adicionar: local horario_escolar horario_user md5
sudo systemctl restart postgresql
```

### Passo 3: Configurar o Projeto

```bash
# Clonar o projeto
git clone https://github.com/seu-usuario/horario-escolar.git
cd horario-escolar

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Configurar variáveis de ambiente
nano .env
```

Conteúdo do arquivo `.env`:
```env
DEBUG=False
SECRET_KEY=sua-chave-secreta-muito-segura-aqui
DATABASE_URL=postgresql://horario_user:sua_senha_segura@localhost/horario_escolar
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
```

### Passo 4: Configurar Django para Produção

```python
# horario_escolar/settings.py
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'horario_escolar'),
        'USER': os.environ.get('DB_USER', 'horario_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Passo 5: Executar Migrações e Coletar Arquivos Estáticos

```bash
# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

### Passo 6: Configurar Gunicorn

```bash
# Criar arquivo de configuração do Gunicorn
nano gunicorn.conf.py
```

Conteúdo do `gunicorn.conf.py`:
```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
user = "www-data"
group = "www-data"
tmp_upload_dir = None
```

### Passo 7: Criar Serviço do Systemd

```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/horario-escolar.service
```

Conteúdo do arquivo de serviço:
```ini
[Unit]
Description=Gerenciador de Horário Escolar
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/horario-escolar
Environment="PATH=/var/www/horario-escolar/venv/bin"
ExecStart=/var/www/horario-escolar/venv/bin/gunicorn --config gunicorn.conf.py horario_escolar.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Recarregar systemd e iniciar serviço
sudo systemctl daemon-reload
sudo systemctl start horario-escolar
sudo systemctl enable horario-escolar
```

### Passo 8: Configurar Nginx

```bash
# Criar configuração do Nginx
sudo nano /etc/nginx/sites-available/horario-escolar
```

Conteúdo da configuração Nginx:
```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /var/www/horario-escolar/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/horario-escolar/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}

server {
    listen 80;
    server_name _;
    return 444;
}
```

```bash
# Ativar site e remover default
sudo ln -s /etc/nginx/sites-available/horario-escolar /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Passo 9: Configurar SSL com Let's Encrypt

```bash
# Instalar Certbot
sudo apt install snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

# Obter certificado
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Configurar renovação automática
sudo crontab -e
# Adicionar: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Passo 10: Configurar Backup

```bash
# Criar script de backup
sudo nano /usr/local/bin/backup-horario.sh
```

Conteúdo do script de backup:
```bash
#!/bin/bash

BACKUP_DIR="/var/backups/horario-escolar"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="horario_escolar"
DB_USER="horario_user"
PROJECT_DIR="/var/www/horario-escolar"

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco de dados
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Backup dos arquivos
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz -C $PROJECT_DIR media/

# Backup do código (opcional)
tar -czf $BACKUP_DIR/code_backup_$DATE.tar.gz -C $PROJECT_DIR --exclude=venv --exclude=*.pyc --exclude=__pycache__ .

# Manter apenas os últimos 7 backups
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "files_backup_*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "code_backup_*.tar.gz" -mtime +7 -delete

echo "Backup concluído: $DATE"
```

```bash
# Tornar executável e configurar cron
sudo chmod +x /usr/local/bin/backup-horario.sh
sudo crontab -e
# Adicionar: 0 2 * * * /usr/local/bin/backup-horario.sh
```

### Passo 11: Configurar Monitoramento

```bash
# Instalar ferramentas de monitoramento
sudo apt install htop iotop ncdu

# Configurar logrotate para logs do Django
sudo nano /etc/logrotate.d/horario-escolar
```

Conteúdo do logrotate:
```
/var/www/horario-escolar/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload horario-escolar
    endscript
}
```

## 🔧 Comandos Úteis para Manutenção

### Verificar status dos serviços
```bash
sudo systemctl status horario-escolar
sudo systemctl status nginx
sudo systemctl status postgresql
```

### Ver logs
```bash
# Logs do Django/Gunicorn
sudo journalctl -u horario-escolar -f

# Logs do Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Atualizar aplicação
```bash
cd /var/www/horario-escolar
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart horario-escolar
```

### Backup manual
```bash
sudo /usr/local/bin/backup-horario.sh
```

## 📊 Monitoramento e Alertas

### Métricas importantes para monitorar:
- Uso de CPU e memória
- Conexões ativas no banco
- Tempo de resposta das páginas
- Taxa de erro das requisições
- Espaço em disco

### Ferramentas recomendadas:
- **Prometheus + Grafana**: Para métricas e dashboards
- **Sentry**: Para monitoramento de erros
- **UptimeRobot**: Para monitoramento de disponibilidade
- **Papertrail**: Para centralização de logs

## 🚨 Plano de Contingência

### Recuperação de emergência:
1. Restaurar backup mais recente do banco
2. Restaurar arquivos estáticos
3. Verificar integridade dos dados
4. Testar funcionalidades críticas

### Contatos de emergência:
- Hospedagem/Cloud provider
- Equipe de desenvolvimento
- Administradores de sistema

## 📈 Otimização de Performance

### Configurações recomendadas:
- **Redis** para cache de sessão e dados
- **CDN** para arquivos estáticos (CloudFlare, AWS CloudFront)
- **Database indexing** para consultas frequentes
- **Compression** habilitada no Nginx

### Comandos de otimização:
```bash
# Otimizar PostgreSQL
sudo -u postgres psql -d horario_escolar -c "VACUUM ANALYZE;"

# Limpar cache do Django
python manage.py clear_cache
```

## 🔒 Segurança

### Checklist de segurança:
- [ ] Firewall configurado (UFW)
- [ ] SSH com chaves, sem senha
- [ ] Atualizações automáticas
- [ ] Fail2Ban instalado
- [ ] SELinux/AppArmor ativo
- [ ] Backups criptografados
- [ ] Monitoramento de intrusão

---

## 🎯 Checklist Final de Produção

- [ ] Servidor provisionado
- [ ] Domínio configurado
- [ ] SSL instalado
- [ ] Banco PostgreSQL configurado
- [ ] Aplicação Django implantada
- [ ] Nginx configurado
- [ ] Gunicorn rodando como serviço
- [ ] Backups automáticos configurados
- [ ] Monitoramento ativo
- [ ] Testes de carga realizados
- [ ] Documentação atualizada

**Status**: ✅ Pronto para produção!