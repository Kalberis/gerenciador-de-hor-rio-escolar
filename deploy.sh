#!/bin/bash

# Script de Deploy Automatizado - Gerenciador de Horário Escolar
# Versão: 1.0
# Data: Janeiro 2026

set -e  # Parar execução em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERRO] $1${NC}" >&2
}

warning() {
    echo -e "${YELLOW}[AVISO] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Verificar se está rodando como root
if [[ $EUID -eq 0 ]]; then
   error "Este script não deve ser executado como root"
   exit 1
fi

# Configurações - ALTERE CONFORME NECESSÁRIO
DOMAIN="seu-dominio.com"
DB_NAME="horario_escolar"
DB_USER="horario_user"
DB_PASSWORD="sua_senha_segura_aqui"
SECRET_KEY="django-insecure-$(openssl rand -hex 32)"
PROJECT_DIR="/var/www/horario-escolar"
REPO_URL="https://github.com/seu-usuario/horario-escolar.git"

log "🚀 Iniciando deploy automatizado do Gerenciador de Horário Escolar"

# Passo 1: Atualizar sistema
log "📦 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Passo 2: Instalar dependências
log "📦 Instalando dependências..."
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server curl git

# Instalar Node.js (opcional)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Passo 3: Configurar PostgreSQL
log "🗄️ Configurando PostgreSQL..."
sudo -u postgres psql << EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME;
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER') THEN
      CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
   END IF;
END
\$\$;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;
EOF

# Configurar PostgreSQL para aceitar conexões locais
sudo sed -i 's/local   all             postgres                                peer/local   all             postgres                                peer\nlocal   '$DB_NAME'        '$DB_USER'                               md5/' /etc/postgresql/12/main/pg_hba.conf
sudo systemctl restart postgresql

# Passo 4: Clonar/Atualizar projeto
if [ -d "$PROJECT_DIR" ]; then
    log "📁 Projeto já existe. Atualizando..."
    cd $PROJECT_DIR
    git pull origin main
else
    log "📁 Clonando projeto..."
    sudo mkdir -p $PROJECT_DIR
    sudo chown -R $USER:$USER $PROJECT_DIR
    git clone $REPO_URL $PROJECT_DIR
    cd $PROJECT_DIR
fi

# Passo 5: Configurar ambiente virtual
log "🐍 Configurando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary python-decouple

# Passo 6: Configurar variáveis de ambiente
log "⚙️ Configurando variáveis de ambiente..."
cat > .env << EOF
DEBUG=False
SECRET_KEY=$SECRET_KEY
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost/$DB_NAME
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=horario_escolar.settings
EOF

# Passo 7: Configurar Django
log "🎯 Configurando Django..."
python manage.py migrate
python manage.py collectstatic --noinput --clear

# Criar superusuário se não existir
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@$DOMAIN', 'admin123')" | python manage.py shell

# Passo 8: Configurar Gunicorn
log "🐴 Configurando Gunicorn..."
cat > gunicorn.conf.py << EOF
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
EOF

# Passo 9: Configurar serviço systemd
log "🔧 Configurando serviço systemd..."
sudo tee /etc/systemd/system/horario-escolar.service > /dev/null << EOF
[Unit]
Description=Gerenciador de Horário Escolar
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --config gunicorn.conf.py horario_escolar.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable horario-escolar

# Passo 10: Configurar Nginx
log "🌐 Configurando Nginx..."
sudo tee /etc/nginx/sites-available/horario-escolar > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$server_name;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}

server {
    listen 80 default_server;
    server_name _;
    return 444;
}
EOF

# Ativar site
sudo ln -sf /etc/nginx/sites-available/horario-escolar /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Passo 11: Configurar SSL (Let's Encrypt)
log "🔒 Configurando SSL..."
if command -v certbot &> /dev/null; then
    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
else
    warning "Certbot não encontrado. Instale manualmente: sudo apt install certbot python3-certbot-nginx"
fi

# Passo 12: Configurar backup
log "💾 Configurando backup..."
sudo tee /usr/local/bin/backup-horario.sh > /dev/null << EOF
#!/bin/bash

BACKUP_DIR="/var/backups/horario-escolar"
DATE=\$(date +%Y%m%d_%H%M%S)
DB_NAME="$DB_NAME"
DB_USER="$DB_USER"
PROJECT_DIR="$PROJECT_DIR"

# Criar diretório de backup
sudo mkdir -p \$BACKUP_DIR
sudo chown \$USER:\$USER \$BACKUP_DIR

# Backup do banco de dados
pg_dump -U $DB_USER -h localhost $DB_NAME > \$BACKUP_DIR/db_backup_\$DATE.sql

# Backup dos arquivos
tar -czf \$BACKUP_DIR/files_backup_\$DATE.tar.gz -C $PROJECT_DIR media/ 2>/dev/null || true

# Manter apenas os últimos 7 backups
find \$BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete 2>/dev/null || true
find \$BACKUP_DIR -name "files_backup_*.tar.gz" -mtime +7 -delete 2>/dev/null || true

echo "Backup concluído: \$DATE"
EOF

sudo chmod +x /usr/local/bin/backup-horario.sh

# Configurar cron para backup diário
(crontab -l ; echo "0 2 * * * /usr/local/bin/backup-horario.sh") | crontab -

# Passo 13: Configurar firewall
log "🔥 Configurando firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
echo "y" | sudo ufw enable

# Passo 14: Configurar logrotate
log "📝 Configurando logrotate..."
sudo tee /etc/logrotate.d/horario-escolar > /dev/null << EOF
$PROJECT_DIR/logs/*.log {
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
EOF

# Passo 15: Iniciar serviços
log "▶️ Iniciando serviços..."
sudo systemctl start horario-escolar
sudo systemctl restart nginx

# Passo 16: Verificar instalação
log "✅ Verificando instalação..."
sleep 5

if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200\|301\|302"; then
    log "🎉 Deploy concluído com sucesso!"
    log "🌐 Acesse: https://$DOMAIN"
    log "👤 Usuário admin: admin"
    log "🔑 Senha admin: admin123"
    log "📧 Altere a senha após o primeiro login!"
else
    error "❌ Erro na verificação. Verifique os logs:"
    error "sudo journalctl -u horario-escolar -n 50"
    error "sudo tail -f /var/log/nginx/error.log"
fi

# Informações finais
cat << EOF

${GREEN}╔══════════════════════════════════════════════════════════════╗
║                      DEPLOY CONCLUÍDO!                       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🌐 URL: https://$DOMAIN                                     ║
║  👤 Admin: admin                                             ║
║  🔑 Senha: admin123                                          ║
║                                                              ║
║  📋 PRÓXIMOS PASSOS:                                         ║
║  1. Acesse o admin e altere a senha                          ║
║  2. Configure as turmas e professores                        ║
║  3. Teste todas as funcionalidades                           ║
║  4. Configure monitoramento                                  ║
║                                                              ║
║  🔧 COMANDOS ÚTEIS:                                          ║
║  • Logs: sudo journalctl -u horario-escolar -f              ║
║  • Restart: sudo systemctl restart horario-escolar           ║
║  • Backup: sudo /usr/local/bin/backup-horario.sh             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝${NC}

EOF