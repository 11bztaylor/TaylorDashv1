# Environment Setup Procedures

**Last Updated:** 2025-09-12
**Version:** 1.0
**Status:** Production Ready Environment

## Development Environment Setup

### Prerequisites
```bash
# Required software
sudo apt update
sudo apt install -y docker.io docker-compose python3 python3-pip nodejs npm git

# Docker permissions
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker-compose --version
python3 --version
node --version
```

### Repository Setup
```bash
# Clone repository
git clone <repository-url> TaylorDashv1
cd TaylorDashv1

# Environment configuration
cp .env.example .env

# Edit .env with development settings
nano .env
```

### Development Environment Configuration
```bash
# .env for development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Database
DATABASE_URL=postgresql://taylordash:taylordash123@postgres:5432/taylordash
DATABASE_POOL_SIZE=10

# Authentication
JWT_SECRET_KEY=dev-secret-key-change-in-production
API_KEY=taylordash-dev-key
SESSION_EXPIRE_HOURS=24

# CORS (development)
CORS_ORIGINS=["http://localhost:5174", "http://localhost:3000"]

# External services
MQTT_BROKER_URL=mqtt://mosquitto:1883
VICTORIA_METRICS_URL=http://victoriametrics:8428
PROMETHEUS_URL=http://prometheus:9090
```

### Service Startup
```bash
# Build and start all services
make up

# Alternative: manual startup
docker-compose up -d --build

# Verify services
docker-compose ps
./ops/validate_p1.sh
```

## Production Environment Setup

### Server Requirements
```bash
# Minimum hardware requirements
# - CPU: 4 cores
# - RAM: 8GB
# - Disk: 100GB SSD
# - Network: 1Gbps

# Recommended for production
# - CPU: 8 cores
# - RAM: 16GB
# - Disk: 200GB SSD
# - Network: 1Gbps with redundancy
```

### System Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker (production version)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose (production version)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# System optimization
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### SSL Certificate Setup
```bash
# Generate self-signed certificate (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/taylordash.key \
  -out certs/taylordash.crt \
  -subj "/CN=localhost"

# Production certificate (Let's Encrypt)
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem certs/taylordash.crt
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem certs/taylordash.key
```

### Production Environment Configuration
```bash
# Production .env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database (production)
DATABASE_URL=postgresql://taylordash:STRONG_PASSWORD@db-server:5432/taylordash_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Security (production)
JWT_SECRET_KEY=CRYPTOGRAPHICALLY_SECURE_SECRET_KEY
API_KEY=PRODUCTION_API_KEY
SESSION_EXPIRE_HOURS=8

# CORS (production)
CORS_ORIGINS=["https://yourdomain.com"]

# External services (production)
MQTT_BROKER_URL=mqtts://mqtt.yourdomain.com:8883
VICTORIA_METRICS_URL=https://metrics.yourdomain.com
PROMETHEUS_URL=https://prometheus.yourdomain.com
```

## Database Setup

### PostgreSQL Installation
```bash
# PostgreSQL via Docker (recommended)
docker run -d --name postgres-prod \
  -e POSTGRES_DB=taylordash \
  -e POSTGRES_USER=taylordash \
  -e POSTGRES_PASSWORD=SECURE_PASSWORD \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:13

# Or system installation
sudo apt install postgresql postgresql-contrib
sudo -u postgres createuser --interactive taylordash
sudo -u postgres createdb taylordash -O taylordash
```

### Database Configuration
```bash
# Connect to database
psql -U taylordash -d taylordash -h localhost

# Verify connection
docker-compose exec postgres psql -U taylordash -d taylordash -c "SELECT version();"

# Run initial migrations
docker-compose exec backend alembic upgrade head

# Verify tables created
docker-compose exec postgres psql -U taylordash -d taylordash -c "\dt"
```

### Database Optimization
```sql
-- Performance tuning
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
SELECT pg_reload_conf();
```

## MQTT Broker Setup

### Mosquitto Configuration
```bash
# Create Mosquitto config
cat > mosquitto/config/mosquitto.conf << EOF
listener 1883 0.0.0.0
allow_anonymous true
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
log_type error
log_type warning
log_type notice
log_type information
EOF

# Start Mosquitto
docker run -d --name mosquitto \
  -p 1883:1883 \
  -v $(pwd)/mosquitto/config:/mosquitto/config \
  -v mosquitto_data:/mosquitto/data \
  -v mosquitto_log:/mosquitto/log \
  eclipse-mosquitto
```

### MQTT Security Setup
```bash
# Create password file for production
docker-compose exec mosquitto mosquitto_passwd -c /mosquitto/config/passwd taylordash

# Update mosquitto.conf for authentication
cat >> mosquitto/config/mosquitto.conf << EOF
allow_anonymous false
password_file /mosquitto/config/passwd
EOF

# Restart with authentication
docker-compose restart mosquitto
```

## Monitoring Setup

### Prometheus Configuration
```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'taylordash-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'victoriametrics'
    static_configs:
      - targets: ['victoriametrics:8428']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres_exporter:9187']
```

### VictoriaMetrics Setup
```bash
# VictoriaMetrics for time series data
docker run -d --name victoriametrics \
  -p 8428:8428 \
  -v victoria_data:/victoria-metrics-data \
  victoriametrics/victoria-metrics:latest \
  --storageDataPath=/victoria-metrics-data \
  --retentionPeriod=1y
```

### Grafana Dashboard Setup
```bash
# Grafana for visualization
docker run -d --name grafana \
  -p 3001:3000 \
  -v grafana_data:/var/lib/grafana \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana:latest

# Add data sources
# - Prometheus: http://prometheus:9090
# - VictoriaMetrics: http://victoriametrics:8428
```

## Load Balancer Setup

### Nginx Configuration
```nginx
# nginx/taylordash.conf
upstream backend {
    server backend:8000;
    # Add multiple backends for scaling
    # server backend2:8000;
    # server backend3:8000;
}

upstream frontend {
    server frontend:5174;
}

server {
    listen 80;
    server_name taylordash.local;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name taylordash.local;

    ssl_certificate /etc/nginx/ssl/taylordash.crt;
    ssl_certificate_key /etc/nginx/ssl/taylordash.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # API routes
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend routes
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Backup and Recovery Setup

### Automated Backup Configuration
```bash
# Create backup script
cat > /usr/local/bin/taylordash_backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/taylordash"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec -T postgres pg_dump -U taylordash taylordash > "$BACKUP_DIR/db_$DATE.sql"

# Configuration backup
cp .env "$BACKUP_DIR/env_$DATE"
cp docker-compose.yml "$BACKUP_DIR/compose_$DATE.yml"

# Compress and encrypt
tar -czf "$BACKUP_DIR/taylordash_backup_$DATE.tar.gz" "$BACKUP_DIR/db_$DATE.sql" "$BACKUP_DIR/env_$DATE" "$BACKUP_DIR/compose_$DATE.yml"
gpg --cipher-algo AES256 --compress-algo 1 --s2k-mode 3 --s2k-digest-algo SHA512 --s2k-count 65536 --symmetric --output "$BACKUP_DIR/taylordash_backup_$DATE.tar.gz.gpg" "$BACKUP_DIR/taylordash_backup_$DATE.tar.gz"

# Cleanup
rm "$BACKUP_DIR/db_$DATE.sql" "$BACKUP_DIR/env_$DATE" "$BACKUP_DIR/compose_$DATE.yml" "$BACKUP_DIR/taylordash_backup_$DATE.tar.gz"

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.gpg" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/taylordash_backup_$DATE.tar.gz.gpg"
EOF

chmod +x /usr/local/bin/taylordash_backup.sh

# Schedule daily backups
echo "0 2 * * * /usr/local/bin/taylordash_backup.sh" | crontab -
```

## Security Hardening

### System Security
```bash
# Firewall configuration
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Fail2ban for SSH protection
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Docker Security
```bash
# Docker daemon security
sudo mkdir -p /etc/docker
cat > /etc/docker/daemon.json << EOF
{
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

sudo systemctl restart docker
```

## Environment Validation

### Development Validation
```bash
# Run full validation suite
./ops/validate_p1.sh

# Expected results:
# - All services healthy
# - API endpoints responding
# - Authentication working
# - Database connectivity confirmed
# - 89%+ pass rate
```

### Production Validation
```bash
# Production health checks
curl -sf https://yourdomain.com/health/ready
curl -sf https://yourdomain.com/api/v1/projects

# Performance validation
ab -n 100 -c 10 https://yourdomain.com/api/v1/projects

# Security validation
nmap -sS -O yourdomain.com
testssl.sh yourdomain.com
```

## Troubleshooting Setup Issues

### Common Setup Problems
```bash
# Docker permission issues
sudo usermod -aG docker $USER
newgrp docker

# Port conflicts
netstat -tlnp | grep -E "(3000|5174|5432|1883)"
sudo lsof -i :3000

# Database connection issues
docker-compose logs postgres
docker-compose exec postgres pg_isready -U taylordash -d taylordash

# SSL certificate issues
openssl verify certs/taylordash.crt
openssl x509 -in certs/taylordash.crt -text -noout
```

### Resource Issues
```bash
# Disk space
df -h
docker system prune -f

# Memory issues
free -h
docker stats --no-stream

# Check service logs
docker-compose logs --tail=100 backend
docker-compose logs --tail=100 postgres
```