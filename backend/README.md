# TaylorDash Backend Architecture

## 🎯 Purpose
FastAPI-based backend implementing a **secure, event-driven, add-only architecture** for extensible plugin systems, real-time data processing, and comprehensive API services.

## 📁 Contents
- **Key Files:**
  - `main.py` - FastAPI application entry point with plugin system
  - `database.py` - PostgreSQL database connection and operations
  - `mqtt_client.py` - MQTT messaging for real-time communication
  - `security.py` - Authentication and authorization utilities
  - `pyproject.toml` - Project dependencies and configuration

- **Directories:**
  - `app/` - Core application modules (routers, models, services)
  - `tests/` - Unit and integration tests
  - `plugins/` - Dynamically loaded plugin storage
  - `test_plugins/` - Plugin security testing environment

## 🔧 Common Tasks
- **Start development server**: `uvicorn app.main:app --reload`
- **Run tests**: `pytest tests/`
- **Install dependencies**: `pip install -e .`
- **Database migrations**: Check `app/database_migrations/`
- **Plugin management**: Use API endpoints in `app/routers/plugins.py`

## 🔗 Dependencies
- Depends on: PostgreSQL database, MQTT broker
- Used by: Frontend React app, external plugin systems
- Integrates with: Prometheus metrics, OpenTelemetry tracing

## 💡 Quick Start for AI Agents
When working in this directory:
1. Check `app/main.py` for API structure and plugin loading
2. Review `app/routers/` for all available endpoints
3. Use `app/models/` for database schema understanding
4. Follow security patterns in `security.py` for auth

## ⚠️ Important Notes
- All plugins are sandboxed for security
- MQTT connections require proper authentication
- Database connections use connection pooling
- CORS is configured for frontend integration