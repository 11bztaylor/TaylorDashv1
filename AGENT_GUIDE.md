# 🤖 TaylorDash Agent Navigation Guide

**🎯 Quick Context:** TaylorDash is a visual, event-driven home lab management system built with FastAPI backend, React frontend, MQTT messaging, and PostgreSQL. It's architected for add-only extensions via plugins and adapters without core modifications.

## 📍 Directory Map

```
/TaylorProjects/TaylorDashv1/
├── backend/                    # FastAPI backend with auth, MQTT, plugins
│   ├── app/                   # Main application code
│   │   ├── main.py           # FastAPI entry point, health checks, CRUD APIs
│   │   ├── routers/          # API endpoint modules (auth, plugins, mcp)
│   │   ├── models/           # Database models
│   │   ├── services/         # Business logic (plugin security, installer)
│   │   ├── database.py       # PostgreSQL connection pool
│   │   ├── mqtt_client.py    # MQTT event publisher/subscriber
│   │   ├── security.py       # API key auth, security headers
│   │   └── schemas.py        # Pydantic models
│   ├── test_plugins/         # Test plugin samples (legitimate/malicious)
│   ├── tests/               # Pytest test suite
│   └── venv/                # Python virtual environment
├── frontend/                  # React + TypeScript + Tailwind UI
│   ├── src/                 # Source code
│   │   ├── components/      # React components (LoginPage, ProjectsList, etc.)
│   │   ├── contexts/        # React contexts (AuthContext)
│   │   ├── services/        # API client, MQTT, event bus
│   │   ├── plugins/         # Plugin registry and management
│   │   ├── pages/           # Page components
│   │   ├── types/           # TypeScript type definitions
│   │   └── App.tsx          # Main React app
│   └── node_modules/        # npm dependencies
├── examples/                  # Sample plugins and extensions
│   ├── midnight-hud/        # Draggable HUD plugin example
│   ├── mcp-manager/         # Model Context Protocol manager
│   └── projects-manager/    # Project management plugin
├── infra/                     # Infrastructure configuration
│   ├── traefik/             # Reverse proxy config
│   ├── postgres/            # Database init scripts
│   ├── mosquitto/           # MQTT broker config
│   ├── prometheus/          # Metrics collection
│   └── grafana/             # Visualization dashboards
├── docs/                      # Diátaxis documentation
├── ops/                       # Operational scripts
├── certs/                     # TLS certificates
└── docker-compose.yml        # Full stack orchestration
```

## 🚀 Quick Start Commands

```bash
# Start full stack
cd /TaylorProjects/TaylorDashv1
docker compose up -d

# Backend development
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development
cd frontend
npm run dev

# Health validation
bash ops/validate_p1.sh

# View logs
docker compose logs -f backend
docker compose logs -f mosquitto
```

## 🔑 Key Environment Variables

- `API_KEY`: Backend authentication (default: taylordash-dev-key)
- `DATABASE_URL`: PostgreSQL connection string
- `MQTT_HOST`: Mosquitto broker hostname
- `MINIO_ROOT_USER/PASSWORD`: Object storage credentials

## 📍 Where to Find What

| Need | Location | Key Files |
|------|----------|-----------|
| **Authentication** | `backend/app/routers/auth.py` | API key verification |
| **API Endpoints** | `backend/app/main.py` | Projects CRUD, events, health |
| **Database Models** | `backend/app/models/` | Plugin, project schemas |
| **MQTT Events** | `backend/app/mqtt_client.py` | Event publishing/subscribing |
| **Plugin System** | `backend/app/routers/plugins.py` | Plugin management API |
| **Frontend Auth** | `frontend/src/contexts/AuthContext.tsx` | User authentication state |
| **API Client** | `frontend/src/services/api.ts` | HTTP client configuration |
| **React Components** | `frontend/src/components/` | UI components library |
| **Plugin Registry** | `frontend/src/plugins/registry.ts` | Frontend plugin management |
| **Infrastructure** | `infra/` | Service configurations |
| **Documentation** | `docs/` | Diátaxis-structured docs |

## 🔄 Common Task Workflows

### Add New API Endpoint
1. Define route in `backend/app/routers/` or `main.py`
2. Add Pydantic schemas in `schemas.py`
3. Implement database operations
4. Add authentication with `verify_api_key`
5. Test with `/api/docs` (Swagger UI)

### Create React Component
1. Add component to `frontend/src/components/`
2. Import and use in `App.tsx` or page components
3. Use Tailwind for styling
4. Connect to API via `services/api.ts`

### Add New Plugin
1. Create plugin in `examples/your-plugin/`
2. Register in `frontend/src/plugins/registry.ts`
3. Add route in `backend/app/routers/plugins.py`
4. Test with plugin security validation

### Debug Issues
1. Check service health: `docker compose ps`
2. Backend logs: `docker compose logs backend`
3. API health: `curl http://localhost:8000/health/ready`
4. MQTT: Check `mosquitto` logs for connection issues
5. Database: Connect with credentials in docker-compose.yml

## 🌐 Service URLs (Local Development)

- **Frontend**: http://localhost:3000 (dev) | https://taylordash.local (prod)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **MQTT**: localhost:1883
- **Prometheus**: localhost:9090
- **Grafana**: localhost:3000 (admin/admin)
- **MinIO**: localhost:9000

## 🤖 For AI Agents

### Your Tools
- **Command**: `docker compose up -d` (start stack)
- **Command**: `bash ops/validate_p1.sh` (health check)
- **Command**: `uvicorn app.main:app --reload` (backend dev)
- **File**: `backend/app/main.py` (main API endpoints)
- **File**: `frontend/src/App.tsx` (main React app)
- **Pattern**: Follow add-only architecture - extend, don't modify core

### Common Pitfalls
- ⚠️ Don't modify core files - use plugin/adapter pattern
- ⚠️ Always use API key authentication (`X-API-Key` header)
- ⚠️ Check service dependencies in docker-compose.yml
- ⚠️ MQTT requires authentication (taylordash/taylordash)
- ⚠️ Database URL format: `postgresql://user:pass@host:port/db`

### Success Criteria
- ✅ All services show "healthy" in `docker compose ps`
- ✅ Backend `/health/ready` returns 200
- ✅ MQTT can publish/subscribe events
- ✅ Frontend connects to backend API
- ✅ Plugin system validates and loads correctly

## 📚 Next Steps

1. Read service-specific quick references: `backend/QUICK_REFERENCE.md`, `frontend/QUICK_REFERENCE.md`
2. Review common tasks: `COMMON_TASKS.md`
3. Use decision trees: `DECISION_TREES.md`
4. Check troubleshooting: `TROUBLESHOOTING_MATRIX.md`
5. Understand integrations: `INTEGRATION_MAP.md`

**🎯 Remember**: TaylorDash follows the add-only principle. Always extend through plugins, adapters, and new services rather than modifying existing core components.