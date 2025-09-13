# Decision Trees Guide

## 🎯 Where Should I Make Changes?

### Adding Authentication Feature
```
Authentication Feature
├── Backend API Logic
│   └── backend/app/routers/auth.py (API endpoints)
├── Frontend State Management
│   └── frontend/src/contexts/AuthContext.tsx (Auth context)
├── Frontend UI Components
│   ├── frontend/src/components/LoginPage.tsx (Login form)
│   └── frontend/src/components/ProtectedRoute.tsx (Route protection)
└── Security Middleware
    └── backend/app/security.py (API key verification)
```

### Adding New API Endpoint
```
Need New API Endpoint?
├── Simple CRUD for existing table?
│   └── Add to backend/app/main.py (with existing patterns)
├── Complex business logic?
│   ├── Create backend/app/routers/your_feature.py
│   └── Add to backend/app/main.py (include router)
├── New data model?
│   ├── Add to backend/app/models/your_model.py
│   ├── Update infra/postgres/init.sql (database schema)
│   └── Create backend/app/routers/your_feature.py
└── Plugin-specific endpoint?
    ├── Add to backend/app/routers/plugins.py
    └── Update examples/your-plugin/plugin.json
```

### Adding New React Component
```
New React Component?
├── Reusable UI component?
│   └── frontend/src/components/YourComponent.tsx
├── Full page component?
│   ├── frontend/src/pages/YourPage.tsx
│   └── frontend/src/App.tsx (add route)
├── Plugin-specific component?
│   ├── examples/your-plugin/src/components/
│   └── examples/your-plugin/src/App.tsx
└── Context/state management?
    ├── frontend/src/contexts/YourContext.tsx
    └── frontend/src/App.tsx (wrap with provider)
```

### Adding New Plugin
```
New Plugin Development
├── Standalone plugin?
│   ├── examples/your-plugin/ (plugin directory)
│   ├── examples/your-plugin/plugin.json (manifest)
│   ├── examples/your-plugin/src/App.tsx (main component)
│   └── frontend/src/plugins/registry.ts (register)
├── Plugin with backend API?
│   ├── backend/app/routers/plugins.py (API endpoints)
│   ├── examples/your-plugin/ (frontend code)
│   └── frontend/src/plugins/registry.ts (register)
└── Plugin with database?
    ├── infra/postgres/init.sql (schema)
    ├── backend/app/models/plugin_models.py (models)
    ├── backend/app/routers/plugins.py (API)
    └── examples/your-plugin/ (frontend)
```

### Database Schema Changes
```
Database Changes?
├── New table for core feature?
│   ├── infra/postgres/init.sql (add CREATE TABLE)
│   ├── backend/app/models/your_model.py (SQLAlchemy model)
│   └── backend/app/main.py (use in API endpoints)
├── New table for plugin?
│   ├── infra/postgres/init.sql (add CREATE TABLE)
│   ├── backend/app/models/plugin_models.py (models)
│   └── backend/app/routers/plugins.py (plugin API)
├── Modify existing table?
│   ├── Create migration SQL file
│   ├── Update backend/app/models/ (corresponding model)
│   └── Update API endpoints that use the table
└── Add indexes for performance?
    └── infra/postgres/init.sql (CREATE INDEX statements)
```

## 🔧 What Technology Should I Use?

### Frontend Development Decisions
```
Frontend Task?
├── Need real-time updates?
│   ├── Use MQTT: frontend/src/services/mqttService.ts
│   └── Use EventBus: frontend/src/services/eventBus.ts
├── Need API communication?
│   ├── Simple request: frontend/src/services/api.ts
│   └── Complex logic: Create custom service
├── Need state management?
│   ├── Component-level: React useState
│   ├── App-level: React Context (frontend/src/contexts/)
│   └── Complex state: Consider Redux Toolkit
├── Need UI components?
│   ├── Use existing: frontend/src/components/
│   ├── Icons: Lucide React
│   └── Styling: Tailwind CSS classes
└── Need routing?
    └── React Router: frontend/src/App.tsx
```

### Backend Development Decisions
```
Backend Task?
├── Need database access?
│   ├── Simple queries: Use asyncpg directly
│   ├── Complex queries: Consider SQLAlchemy
│   └── Connection: backend/app/database.py (pool)
├── Need authentication?
│   ├── API endpoints: backend/app/security.py
│   └── Dependencies: Depends(verify_api_key)
├── Need real-time events?
│   ├── MQTT publishing: backend/app/mqtt_client.py
│   └── Event schemas: Define in backend/app/schemas.py
├── Need file storage?
│   ├── Object storage: MinIO (configured in docker-compose.yml)
│   └── Temporary files: Local filesystem
└── Need background tasks?
    ├── Simple: asyncio.create_task()
    └── Complex: Consider Celery or similar
```

### Infrastructure Decisions
```
Infrastructure Need?
├── New service in stack?
│   ├── Add to docker-compose.yml
│   ├── Configure in infra/your-service/
│   └── Update networking and health checks
├── Need monitoring?
│   ├── Metrics: Prometheus (infra/prometheus/)
│   ├── Logs: Structured logging (backend/app/logging_utils.py)
│   └── Visualization: Grafana (infra/grafana/)
├── Need reverse proxy rules?
│   └── infra/traefik/ (routing configuration)
└── Need TLS certificates?
    └── certs/ (certificate storage)
```

## 🚨 Error Handling Decisions

### When Something Goes Wrong
```
Error Occurred?
├── Backend API error?
│   ├── Check logs: docker compose logs backend
│   ├── Database issue?
│   │   ├── Check connection: docker compose logs postgres
│   │   └── Check queries: backend/app/main.py
│   ├── MQTT issue?
│   │   ├── Check broker: docker compose logs mosquitto
│   │   └── Check client: backend/app/mqtt_client.py
│   └── Authentication issue?
│       └── Check API key: backend/app/security.py
├── Frontend error?
│   ├── Check browser console
│   ├── Network errors?
│   │   ├── Check API endpoints
│   │   └── Check CORS settings
│   ├── Component errors?
│   │   └── Check ErrorBoundary: frontend/src/components/ErrorBoundary.tsx
│   └── State management issues?
│       └── Check contexts: frontend/src/contexts/
├── Database error?
│   ├── Connection issues?
│   │   ├── Check DATABASE_URL environment variable
│   │   └── Check PostgreSQL service status
│   ├── Query errors?
│   │   ├── Check SQL syntax
│   │   └── Check data types and constraints
│   └── Performance issues?
│       └── Check indexes and query optimization
└── MQTT error?
    ├── Connection refused?
    │   ├── Check mosquitto service
    │   └── Check credentials (taylordash/taylordash)
    ├── Message not received?
    │   ├── Check topic subscription
    │   └── Check message format
    └── Publishing failed?
        ├── Check topic permissions
        └── Check payload format
```

## 🔍 Debugging Strategy

### Performance Issues
```
Performance Problem?
├── Backend slow?
│   ├── Database queries slow?
│   │   ├── Add database indexes
│   │   ├── Optimize query structure
│   │   └── Check connection pool settings
│   ├── API response slow?
│   │   ├── Add caching
│   │   ├── Optimize business logic
│   │   └── Check async/await usage
│   └── Memory usage high?
│       ├── Check connection cleanup
│       └── Profile with memory tools
├── Frontend slow?
│   ├── Large bundle size?
│   │   ├── Check npm bundle analyzer
│   │   └── Implement code splitting
│   ├── Re-rendering issues?
│   │   ├── Use React.memo
│   │   ├── Optimize useEffect dependencies
│   │   └── Check state updates
│   └── Network requests slow?
│       ├── Implement request caching
│       └── Batch API calls
└── Infrastructure slow?
    ├── Container resource limits?
    │   └── Check docker-compose.yml resource allocation
    ├── Network latency?
    │   └── Check service communication
    └── Disk I/O issues?
        └── Check volume configurations
```

### Security Considerations
```
Security Enhancement?
├── API security?
│   ├── Authentication: backend/app/security.py
│   ├── Input validation: backend/app/schemas.py
│   ├── Rate limiting: Consider middleware
│   └── HTTPS: infra/traefik/ configuration
├── Frontend security?
│   ├── XSS protection: Sanitize inputs
│   ├── CSRF protection: API key headers
│   └── Content Security Policy: Add headers
├── Database security?
│   ├── SQL injection: Use parameterized queries
│   ├── Access control: Database user permissions
│   └── Encryption: Consider column encryption
└── Plugin security?
    ├── Validation: backend/app/services/plugin_security.py
    ├── Sandboxing: Plugin execution environment
    └── Permissions: Plugin manifest validation
```

## 🤖 For AI Agents

### Quick Context
Use these decision trees to determine the correct location and approach for implementing new features or fixing issues. Follow the add-only principle and existing patterns.

### Your Tools
- **Decision**: Follow the tree structure to find the right file/location
- **Pattern**: Use existing code patterns in the identified files
- **Validation**: Use `bash ops/validate_p1.sh` to verify changes
- **Documentation**: Check relevant QUICK_REFERENCE.md files

### Common Pitfalls
- ⚠️ Skipping the decision tree and modifying random files
- ⚠️ Not following existing patterns in the codebase
- ⚠️ Adding features without proper error handling
- ⚠️ Not considering security implications of changes
- ⚠️ Forgetting to update related documentation

### Success Criteria
- ✅ Changes follow the decision tree guidance
- ✅ New code matches existing patterns and style
- ✅ Proper error handling and security measures in place
- ✅ All related files updated consistently
- ✅ Validation script passes after changes
- ✅ No breaking changes to existing functionality