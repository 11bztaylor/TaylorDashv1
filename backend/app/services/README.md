# Business Logic Services

## 🎯 Purpose
Service layer containing business logic, external integrations, and complex operations isolated from API routing concerns.

## 📁 Contents
- **Key Files:**
  - Plugin management services (validation, installation, security)
  - Authentication services (JWT handling, user management)
  - Dashboard data aggregation services
  - MQTT message processing services
  - External API integration services

## 🔧 Common Tasks
- **Create new service**: Implement class with clear interface
- **Handle business logic**: Separate from API route handling
- **Integrate external APIs**: Use proper error handling and timeouts
- **Process data**: Transform between database and API formats
- **Validate operations**: Implement business rule validation

## 🔗 Dependencies
- Depends on: Database models, external APIs, configuration
- Used by: API routers, background tasks, plugin system
- Integrates with: Authentication, logging, error handling

## 💡 Quick Start for AI Agents
When working in this directory:
1. Create service classes with dependency injection
2. Separate business logic from data access
3. Use async/await for I/O operations
4. Implement proper error handling and logging
5. Write unit tests for complex business logic

## ⚠️ Important Notes
- Services should be stateless and testable
- Use dependency injection for external dependencies
- Handle errors gracefully with meaningful messages
- Plugin services require additional security validation