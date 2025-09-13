# Data Models

## 🎯 Purpose
SQLAlchemy database models defining schema, relationships, and data validation for the TaylorDash application.

## 📁 Contents
- **Key Files:**
  - `__init__.py` - Model imports and base configuration
  - User models with authentication fields
  - Plugin models with metadata and configuration
  - Dashboard models for layout and settings
  - Log models for audit trails and monitoring

## 🔧 Common Tasks
- **Create new model**: Inherit from Base, define columns and relationships
- **Add relationships**: Use SQLAlchemy relationship() and foreign keys
- **Define validation**: Use column constraints and validators
- **Create migration**: Generate Alembic migration after model changes
- **Query data**: Use session.query() or async session methods

## 🔗 Dependencies
- Depends on: SQLAlchemy, PostgreSQL database schema
- Used by: API services, database operations, migrations
- Integrates with: Authentication system, plugin validation

## 💡 Quick Start for AI Agents
When working in this directory:
1. Follow existing model patterns for consistency
2. Define proper relationships with cascade options
3. Add validation constraints at database level
4. Use appropriate column types for data
5. Document model relationships and constraints

## ⚠️ Important Notes
- Model changes require database migrations
- Use appropriate indexes for query performance
- Sensitive data must be properly encrypted
- Plugin models require security validation fields