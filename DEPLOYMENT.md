# 🚀 Production Deployment Guide

## Pre-Deployment Checklist

- [ ] PostgreSQL database configured
- [ ] OpenAI API key obtained
- [ ] Domain name registered (optional)
- [ ] SSL certificates ready
- [ ] Server/hosting environment provisioned
- [ ] Environment variables prepared
- [ ] Backup strategy defined

## Deployment Options

### Option 1: Traditional Server Deployment

### Option 2: Docker Deployment (Recommended)

### Option 3: Cloud Platform (AWS/GCP/Azure)

---

## Option 1: Traditional Server (Ubuntu/Debian)

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.9 python3-pip python3-venv postgresql nginx redis-server nodejs npm git

# Install Node.js 16+
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs
```

### 2. PostgreSQL Setup

```bash
# Configure PostgreSQL
sudo -u postgres psql

CREATE DATABASE onedevelopment_agent;
CREATE USER agentuser WITH PASSWORD 'StrongPassword123!';
ALTER ROLE agentuser SET client_encoding TO 'utf8';
ALTER ROLE agentuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE agentuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE onedevelopment_agent TO agentuser;
\q

# Enable PostgreSQL on boot
sudo systemctl enable postgresql
```

### 3. Application Deployment

```bash
# Create application user
sudo useradd -m -s /bin/bash onedevelopment
sudo su - onedevelopment

# Clone repository
cd /home/onedevelopment
git clone <your-repo-url> app
cd app

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Create production .env
cat > .env << EOF
DEBUG=False
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

DB_NAME=onedevelopment_agent
DB_USER=agentuser
DB_PASSWORD=StrongPassword123!
DB_HOST=localhost
DB_PORT=5432

OPENAI_API_KEY=your-openai-api-key
REDIS_URL=redis://localhost:6379/0
EOF

# Run migrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py init_data

# Create superuser
python manage.py createsuperuser
```

### 4. Gunicorn Setup

```bash
# Create Gunicorn config
cat > /home/onedevelopment/app/backend/gunicorn_config.py << EOF
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 120
accesslog = "/home/onedevelopment/app/logs/gunicorn_access.log"
errorlog = "/home/onedevelopment/app/logs/gunicorn_error.log"
loglevel = "info"
EOF

# Create logs directory
mkdir -p /home/onedevelopment/app/logs

# Create systemd service
sudo cat > /etc/systemd/system/onedevelopment-backend.service << EOF
[Unit]
Description=OneDevelopment Agent Backend
After=network.target postgresql.service

[Service]
Type=notify
User=onedevelopment
Group=onedevelopment
WorkingDirectory=/home/onedevelopment/app/backend
Environment="PATH=/home/onedevelopment/app/backend/venv/bin"
ExecStart=/home/onedevelopment/app/backend/venv/bin/gunicorn config.wsgi:application -c gunicorn_config.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable onedevelopment-backend
sudo systemctl start onedevelopment-backend
sudo systemctl status onedevelopment-backend
```

### 5. Frontend Build

```bash
cd /home/onedevelopment/app/frontend

# Install dependencies
npm install

# Create production .env
echo "REACT_APP_API_URL=https://your-domain.com/api" > .env

# Build for production
npm run build
```

### 6. Nginx Configuration

```bash
sudo cat > /etc/nginx/sites-available/onedevelopment << EOF
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Frontend
    location / {
        root /home/onedevelopment/app/frontend/build;
        try_files \$uri \$uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }
    
    # Django Admin
    location /admin/ {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Static files
    location /static/ {
        alias /home/onedevelopment/app/backend/staticfiles/;
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/onedevelopment /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## Option 2: Docker Deployment

### 1. Create Dockerfile for Backend

```bash
cat > /home/ec2-user/OneDevelopment-Agent/backend/Dockerfile << EOF
FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
EOF
```

### 2. Create Dockerfile for Frontend

```bash
cat > /home/ec2-user/OneDevelopment-Agent/frontend/Dockerfile << EOF
FROM node:16-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF
```

### 3. Docker Compose

```bash
cat > /home/ec2-user/OneDevelopment-Agent/docker-compose.yml << EOF
version: '3.8'

services:
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: onedevelopment_agent
      POSTGRES_USER: agentuser
      POSTGRES_PASSWORD: securepassword
    ports:
      - "5432:5432"
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  backend:
    build: ./backend
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - ./backend:/app
      - static_volume:/app/staticfiles
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DB_NAME=onedevelopment_agent
      - DB_USER=agentuser
      - DB_PASSWORD=securepassword
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
  static_volume:
EOF

# Deploy
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py init_data
```

---

## Post-Deployment Tasks

### 1. Data Ingestion

```bash
# SSH into server
ssh user@your-server

# Activate virtual environment
cd /home/onedevelopment/app/backend
source venv/bin/activate

# Run data ingestion
python manage.py shell

from agent.data_ingestor import OneDevelopmentDataIngestor
from agent.langgraph_agent import OneDevelopmentAgent
from agent.models import KnowledgeBase

ingestor = OneDevelopmentDataIngestor()
agent = OneDevelopmentAgent()

# Scrape website
data = ingestor.scrape_website(max_pages=50)

# Store in database and vector store
for item in data:
    kb = KnowledgeBase.objects.create(
        source_type=item.get('source_type', 'website'),
        source_url=item.get('url'),
        title=item.get('title', 'Untitled'),
        content=item.get('content', ''),
        summary=item.get('content', '')[:500],
        metadata=item
    )
    agent.add_knowledge(item.get('content', ''), metadata=item)
```

### 2. Monitoring Setup

```bash
# Install monitoring tools
pip install sentry-sdk

# Add to settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
)
```

### 3. Backup Configuration

```bash
# Create backup script
cat > /home/onedevelopment/backup.sh << EOF
#!/bin/bash

BACKUP_DIR="/home/onedevelopment/backups"
DATE=\$(date +%Y%m%d_%H%M%S)

# Backup database
pg_dump -U agentuser onedevelopment_agent > \$BACKUP_DIR/db_\$DATE.sql

# Backup vector store
tar -czf \$BACKUP_DIR/chroma_\$DATE.tar.gz /path/to/chroma_db

# Keep only last 7 days
find \$BACKUP_DIR -name "*.sql" -mtime +7 -delete
find \$BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /home/onedevelopment/backup.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /home/onedevelopment/backup.sh
```

### 4. Performance Tuning

**PostgreSQL:**
```bash
sudo nano /etc/postgresql/13/main/postgresql.conf

# Adjust based on server resources
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB

sudo systemctl restart postgresql
```

**Nginx:**
```bash
sudo nano /etc/nginx/nginx.conf

worker_processes auto;
worker_connections 1024;

# Add to http block
client_max_body_size 10M;
keepalive_timeout 65;
gzip_comp_level 6;
```

### 5. Security Hardening

```bash
# Firewall setup
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Disable root login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart sshd
```

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor logs for errors
- Check disk space
- Review API usage

**Weekly:**
- Review database performance
- Check backup integrity
- Update suggested questions

**Monthly:**
- Update dependencies
- Security patches
- Performance optimization

### Log Management

```bash
# Rotate logs
sudo nano /etc/logrotate.d/onedevelopment

/home/onedevelopment/app/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 onedevelopment onedevelopment
    sharedscripts
    postrotate
        systemctl reload onedevelopment-backend > /dev/null
    endscript
}
```

### Monitoring Commands

```bash
# Check backend status
sudo systemctl status onedevelopment-backend

# View logs
tail -f /home/onedevelopment/app/logs/gunicorn_error.log

# Check database connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Monitor resource usage
htop
```

---

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
sudo journalctl -u onedevelopment-backend -n 50

# Test Gunicorn manually
cd /home/onedevelopment/app/backend
source venv/bin/activate
gunicorn config.wsgi:application --bind 127.0.0.1:8000
```

### Database Connection Issues

```bash
# Test connection
psql -U agentuser -d onedevelopment_agent -h localhost

# Check PostgreSQL status
sudo systemctl status postgresql

# View PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

### High Memory Usage

```bash
# Identify processes
ps aux --sort=-%mem | head

# Adjust Gunicorn workers
# Edit gunicorn_config.py
workers = 2  # Reduce if needed
```

---

## Scaling Strategies

### Horizontal Scaling

1. **Load Balancer:**
   - Use Nginx or HAProxy
   - Multiple backend instances
   - Session persistence

2. **Database:**
   - Read replicas
   - Connection pooling
   - Query optimization

3. **Caching:**
   - Redis for API responses
   - CDN for static files
   - Browser caching

### Vertical Scaling

- Increase server resources
- Optimize database configuration
- Upgrade PostgreSQL version

---

## Rollback Procedure

```bash
# 1. Stop services
sudo systemctl stop onedevelopment-backend
sudo systemctl stop nginx

# 2. Restore database
psql -U agentuser onedevelopment_agent < /home/onedevelopment/backups/db_YYYYMMDD.sql

# 3. Restore code
cd /home/onedevelopment/app
git checkout <previous-commit>

# 4. Reinstall dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 5. Rebuild frontend
cd ../frontend
npm install
npm run build

# 6. Restart services
sudo systemctl start onedevelopment-backend
sudo systemctl start nginx
```

---

**Your One Development AI Agent is now deployed! 🎉**

