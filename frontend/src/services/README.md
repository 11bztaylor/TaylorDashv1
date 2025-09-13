# API Services

## 🎯 Purpose
Service layer for API communication, data fetching, and external integrations with proper error handling and type safety.

## 📁 Contents
- **Service Modules:**
  - API client configuration and base methods
  - Authentication service (login, logout, token management)
  - Plugin service (install, manage, configure plugins)
  - Dashboard service (layout, widgets, data fetching)
  - WebSocket service (real-time messaging, subscriptions)

## 🔧 Common Tasks
- **Make API call**: Use configured service methods
- **Handle authentication**: Attach JWT tokens to requests
- **Error handling**: Implement proper error catching and user feedback
- **Data transformation**: Convert API responses to frontend types
- **Cache management**: Use React Query for caching and synchronization

## 🔗 Dependencies
- Depends on: Fetch API, authentication tokens, TypeScript types
- Used by: Components, pages, React Query hooks
- Integrates with: Backend API, WebSocket connections, error handling

## 💡 Quick Start for AI Agents
When working in this directory:
1. Use centralized API configuration for base URLs
2. Implement proper TypeScript return types
3. Add request/response interceptors for auth
4. Handle network errors and timeouts gracefully
5. Use React Query for data fetching and caching

## ⚠️ Important Notes
- All API calls must include proper authentication
- Handle offline scenarios gracefully
- Plugin API calls require additional security validation
- Implement proper retry logic for failed requests