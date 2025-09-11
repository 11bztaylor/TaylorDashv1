# Infrastructure Quick Troubleshooting

5-minute fixes for common TaylorDash infrastructure issues.

## Prerequisites Check

```bash
# Before running docker compose
docker --version              # Verify Docker is installed
docker compose version        # Test command variation
netstat -tulpn | grep :1883   # Check for MQTT port conflicts
```

## Command Variations

**Docker Compose Commands**:
```bash
# Try these in order if one fails:
docker compose up -d          # Modern Docker CLI
docker-compose up -d          # Legacy standalone tool
```

**If `docker compose` not found**:
```bash
# Install Docker Compose V2
sudo apt-get update && sudo apt-get install docker-compose-plugin
```

## Common Port Conflicts

**MQTT Port 1883 busy**:
```bash
# Find process using port
sudo lsof -i :1883
sudo netstat -tulpn | grep :1883

# Kill conflicting process
sudo kill -9 <PID>

# Or use different port in docker-compose.yml
ports:
  - "1884:1883"  # Change external port
```

**Other common conflicts**:
- Port 80/443: Stop nginx/apache
- Port 5432: Stop local PostgreSQL
- Port 8080: Stop other Traefik instances

## Service Startup Order

Services have dependencies. If startup fails:

```bash
# Start core services first
docker compose up -d postgres mosquitto

# Wait for health checks, then start dependent services
docker compose up -d backend

# Finally start frontend services
docker compose up -d traefik
```

## Health Check Verification

**Quick validation**:
```bash
# Check all services
docker compose ps

# Test individual services
curl -f http://localhost:8000/health/ready    # Backend
mosquitto_pub -h localhost -t test -m hello   # MQTT
```

**Service-specific checks**:
```bash
# PostgreSQL
docker compose exec postgres pg_isready -U taylordash

# MQTT (with auth)
mosquitto_pub -h localhost -t test -m health -u taylordash -P taylordash

# Backend API
curl http://localhost:8000/docs
```

## One-Line Fixes

**Container won't start**:
```bash
docker compose down && docker compose up -d
```

**Port binding error**:
```bash
sudo lsof -ti:1883 | xargs sudo kill -9
```

**Database connection failed**:
```bash
docker compose restart postgres && sleep 5 && docker compose restart backend
```

**Permission denied (volumes)**:
```bash
sudo chown -R $USER:$USER ./infra/ ./certs/
```

**MQTT authentication failed**:
```bash
# Reset MQTT password file
echo "taylordash:taylordash" > infra/mosquitto/password_file
docker compose restart mosquitto
```

## Common Failure Modes

**Backend fails to connect to DB**:
- Check `POSTGRES_PASSWORD` in .env
- Verify postgres is healthy: `docker compose ps postgres`
- Restart in order: postgres → backend

**MQTT connection refused**:
- Port 1883 conflict (see above)
- Check mosquitto.conf allows connections
- Verify user/password in password_file

**Traefik 404 errors**:
- Check labels in docker-compose.yml
- Verify host entries: `tracker.local` → 127.0.0.1
- Restart traefik: `docker compose restart traefik`

**Build failures**:
- Clear build cache: `docker compose build --no-cache backend`
- Check Dockerfile syntax in ./backend/

## Emergency Reset

**Nuclear option** (loses all data):
```bash
docker compose down -v
docker system prune -f
docker volume prune -f
rm -rf certs/ infra/grafana/ infra/postgres/ infra/timescale/ infra/traefik/
docker compose up -d
```

## Validation Script

Run the full validation:
```bash
bash ops/validate_p1.sh
```

Specific checks:
```bash
# Health checks only
docker compose ps

# API endpoints
curl -s http://localhost:8000/health/ready | jq .

# MQTT pub/sub test
mosquitto_sub -h localhost -t test/echo -u taylordash -P taylordash &
mosquitto_pub -h localhost -t test/echo -m "hello" -u taylordash -P taylordash
```