# Backend App Core

## 🎯 Purpose
Core application modules containing business logic, API routes, database models, and services for the TaylorDash backend.

## 📁 Contents
- **Key Files:**
  - `main.py` - FastAPI app initialization, middleware, plugin loader
  - `database.py` - Database connection, session management
  - `schemas.py` - Pydantic models for API serialization
  - `security.py` - JWT authentication, permission decorators
  - `logging_middleware.py` - Request/response logging
  - `mqtt_client.py` - Real-time messaging integration

- **Directories:**
  - `routers/` - API endpoint definitions grouped by feature
  - `models/` - SQLAlchemy database models
  - `services/` - Business logic and external integrations
  - `database/` - Database utilities and helpers
  - `core/` - Core configuration and utilities

## 🔧 Common Tasks
- **Add new API endpoint**: Create router in `routers/`, register in `main.py`
- **Define data model**: Add SQLAlchemy model in `models/`
- **Add business logic**: Create service class in `services/`
- **Database operations**: Use utilities in `database/`
- **Configure authentication**: Modify decorators in `security.py`

## 🔗 Dependencies
- Depends on: Database schema, MQTT broker configuration
- Used by: Frontend API calls, plugin system hooks
- Integrates with: Authentication middleware, logging system

## 💡 Quick Start for AI Agents
When working in this directory:
1. Start with `main.py` to understand app structure
2. Check `routers/` for existing API patterns
3. Review `models/` for data relationships
4. Use `services/` for reusable business logic
5. Follow authentication patterns in `security.py`

## ⚠️ Important Notes
- All routes require proper error handling
- Database sessions must be properly closed
- Plugin hooks are defined in main.py
- CORS settings configured for frontend access