# Troubleshooting Matrix

## 🚨 Quick Symptom Diagnosis

| Symptom | Check | Solution | File/Command |
|---------|-------|----------|--------------|
| **API returns 401 Unauthorized** | API key header | Add `X-API-Key: taylordash-dev-key` header | `backend/app/security.py` |
| **API returns 500 Internal Server Error** | Backend logs | Check `docker compose logs backend` | `backend/app/main.py` |
| **Database connection error** | DATABASE_URL | Check connection string and PostgreSQL status | `.env`, `docker-compose.yml` |
| **MQTT connection failed** | MQTT broker | Restart mosquitto: `docker compose restart mosquitto` | `infra/mosquitto/` |
| **Frontend shows blank screen** | Console errors | Check browser dev tools console | `frontend/src/App.tsx` |
| **Can't connect to backend** | Service status | Run `docker compose ps` | `docker-compose.yml` |
| **Login page shows error** | AuthContext | Check authentication state and API calls | `frontend/src/contexts/AuthContext.tsx` |
| **Plugins not loading** | Plugin registry | Check plugin registration and manifests | `frontend/src/plugins/registry.ts` |
| **Real-time updates not working** | MQTT service | Check MQTT client and subscriptions | `frontend/src/services/mqttService.ts` |
| **Slow database queries** | Missing indexes | Add indexes to frequently queried columns | `infra/postgres/init.sql` |

## 🔧 Service-Specific Troubleshooting

### Backend Issues

| Problem | Diagnosis | Solution |
|---------|-----------|----------|
| **Server won't start** | Check `docker compose logs backend` | Fix Python imports, environment variables |
| **Database queries failing** | Check PostgreSQL connection | Verify DATABASE_URL, restart postgres service |
| **MQTT publishing fails** | Check MQTT client logs | Verify MQTT credentials, restart mosquitto |
| **API responses slow** | Profile database queries | Add indexes, optimize query structure |
| **Memory usage high** | Check connection pooling | Review database connection cleanup |

```bash
# Backend debugging commands
docker compose logs -f backend                    # View live logs
docker compose exec backend python -c "import app.main"  # Test imports
curl -H "X-API-Key: taylordash-dev-key" http://localhost:8000/health/ready  # Health check
```

### Frontend Issues

| Problem | Diagnosis | Solution |
|---------|-----------|----------|
| **White screen of death** | Browser console errors | Fix JavaScript errors, check imports |
| **API calls failing** | Network tab in dev tools | Check API endpoints, CORS settings |
| **Components not rendering** | React error boundaries | Check component props and state |
| **Routing not working** | React Router setup | Verify route configuration |
| **Styles not loading** | Tailwind CSS build | Check build process and CSS imports |

```bash
# Frontend debugging commands
npm run type-check                               # TypeScript errors
npm run lint                                     # ESLint warnings
docker compose logs -f frontend                  # View build logs
curl http://localhost:3000                       # Test frontend availability
```

### Database Issues

| Problem | Diagnosis | Solution |
|---------|-----------|----------|
| **Connection refused** | PostgreSQL service status | `docker compose restart postgres` |
| **Permission denied** | Database user permissions | Check user roles and grants |
| **Table doesn't exist** | Schema initialization | Run init.sql scripts |
| **Query timeout** | Long-running queries | Add indexes, optimize queries |
| **Disk space full** | Volume usage | Clean up old data, expand volumes |

```bash
# Database debugging commands
docker compose exec postgres psql -U taylordash -d taylordash  # Connect to DB
docker compose exec postgres pg_isready -U taylordash          # Check readiness
docker volume ls | grep postgres                               # Check volumes
docker system df                                               # Check disk usage
```

### MQTT Issues

| Problem | Diagnosis | Solution |
|---------|-----------|----------|
| **Broker not responding** | Mosquitto service logs | `docker compose restart mosquitto` |
| **Authentication failed** | Username/password | Check credentials in docker-compose.yml |
| **Messages not delivered** | Topic permissions | Verify topic access and subscriptions |
| **Connection drops** | Network stability | Check container networking |
| **High memory usage** | Message retention | Configure message retention policies |

```bash
# MQTT debugging commands
mosquitto_pub -h localhost -t "test" -m "hello" -u taylordash -P taylordash  # Test publish
mosquitto_sub -h localhost -t "#" -u taylordash -P taylordash               # Monitor all topics
docker compose exec mosquitto mosquitto_passwd -U /mosquitto/config/password_file  # Check users
docker compose logs -f mosquitto                                           # View broker logs
```

## 🌐 Network & Infrastructure Issues

### Docker Compose Problems

| Symptom | Check | Solution |
|---------|-------|----------|
| **Services won't start** | `docker compose ps` | Check service dependencies and health checks |
| **Port conflicts** | `netstat -tulpn` | Change port mappings in docker-compose.yml |
| **Volume mount errors** | File permissions | Fix file ownership and permissions |
| **Network isolation** | Container networking | Check network configuration |
| **Resource limits** | System resources | Increase Docker resource allocation |

### Traefik (Reverse Proxy) Issues

| Problem | Diagnosis | Solution |
|---------|-----------|----------|
| **404 Not Found** | Traefik dashboard | Check routing rules and service labels |
| **TLS certificate errors** | Certificate validity | Regenerate certificates in certs/ |
| **Service not reachable** | Service health | Verify backend service is healthy |
| **CORS errors** | CORS configuration | Update CORS settings in backend |

### Performance Issues

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| **Slow page loads** | Large JavaScript bundles | Implement code splitting |
| **High CPU usage** | Inefficient queries | Optimize database queries |
| **Memory leaks** | Uncleaned resources | Review connection cleanup |
| **Network timeouts** | Service overload | Scale services or add caching |

## 🔐 Security Issues

### Authentication Problems

| Problem | Check | Solution |
|---------|-------|----------|
| **API key not working** | Key validity | Verify API_KEY environment variable |
| **Session expired** | Token storage | Check localStorage session token |
| **CORS blocked** | Origin headers | Update allowed origins in backend |
| **Unauthorized access** | Role permissions | Verify user roles and route protection |

### Plugin Security Issues

| Problem | Check | Solution |
|---------|-------|----------|
| **Plugin installation fails** | Security validation | Check plugin manifest and security scan |
| **Plugin not loading** | Registry configuration | Verify plugin registration |
| **Sandbox violations** | Plugin permissions | Review plugin permission model |

## 🔄 Recovery Procedures

### Complete System Reset

```bash
# Nuclear option - resets everything
docker compose down
docker system prune -a --volumes
docker compose up -d
```

### Database Reset

```bash
# Reset only database (WARNING: Data loss)
docker compose down
docker volume rm taylordashv1_postgres_data
docker compose up postgres -d
```

### Service Restart Sequence

```bash
# Graceful restart in dependency order
docker compose restart postgres
sleep 10
docker compose restart mosquitto
sleep 5
docker compose restart backend
sleep 5
docker compose restart frontend
```

### Log Collection

```bash
# Collect all logs for debugging
mkdir -p debug-logs
docker compose logs postgres > debug-logs/postgres.log
docker compose logs mosquitto > debug-logs/mosquitto.log
docker compose logs backend > debug-logs/backend.log
docker compose logs frontend > debug-logs/frontend.log
docker compose logs traefik > debug-logs/traefik.log
```

## 📊 Health Check Commands

### Quick Health Assessment

```bash
# Run the validation script
bash ops/validate_p1.sh

# Manual health checks
curl -s http://localhost:8000/health/ready | jq .
curl -s -H "X-API-Key: taylordash-dev-key" http://localhost:8000/api/v1/health/stack | jq .

# Service status
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

### Performance Monitoring

```bash
# Container resource usage
docker stats --no-stream

# Database connections
docker compose exec postgres psql -U taylordash -d taylordash -c "SELECT count(*) FROM pg_stat_activity;"

# MQTT connections
docker compose exec mosquitto mosquitto_passwd -c /dev/stdout test | wc -l
```

## 🤖 For AI Agents

### Quick Context
This matrix provides symptom-based troubleshooting for TaylorDash. Start with the symptom you observe, follow the diagnosis steps, and apply the solution. Always check logs first.

### Your Tools
- **Command**: `docker compose logs <service>` (check service logs)
- **Command**: `bash ops/validate_p1.sh` (comprehensive health check)
- **Command**: `docker compose ps` (service status)
- **File**: Check the specific files mentioned in solutions

### Common Pitfalls
- ⚠️ Not checking logs before making changes
- ⚠️ Restarting services without understanding the root cause
- ⚠️ Making multiple changes simultaneously
- ⚠️ Not verifying the fix with health checks
- ⚠️ Ignoring dependency order during service restarts

### Success Criteria
- ✅ Symptom is resolved and doesn't reoccur
- ✅ All health checks pass after fix
- ✅ Root cause is identified and documented
- ✅ No new issues introduced by the fix
- ✅ System performance remains stable
- ✅ Logs show normal operation patterns