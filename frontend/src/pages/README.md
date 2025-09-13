# Page Components

## 🎯 Purpose
Top-level page components that represent different routes and views in the TaylorDash application.

## 📁 Contents
- **Key Pages:**
  - Dashboard page with widget grid and customization
  - Plugin management page for installation and configuration
  - Settings page for user preferences and system config
  - Authentication pages (login, register)
  - Plugin-specific pages and embedded views

## 🔧 Common Tasks
- **Add new page**: Create component and add to App.tsx router
- **Handle routing**: Use React Router for navigation
- **Page layout**: Implement consistent header/sidebar structure
- **Data fetching**: Use services and React Query for API calls
- **State management**: Use contexts for page-level state

## 🔗 Dependencies
- Depends on: React Router, components, services, contexts
- Used by: Application routing, user navigation
- Integrates with: Authentication, plugin system, API services

## 💡 Quick Start for AI Agents
When working in this directory:
1. Use React Router for navigation between pages
2. Implement consistent layout patterns
3. Handle authentication requirements per page
4. Use loading states while fetching data
5. Add proper page titles and meta information

## ⚠️ Important Notes
- Protected pages require authentication
- Plugin pages are isolated and secured
- Handle browser back/forward navigation
- Implement proper error boundaries for pages