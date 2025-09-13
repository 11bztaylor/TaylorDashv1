# Frontend Source Code

## 🎯 Purpose
React application source code with TypeScript, organized into components, pages, services, and utilities for modular development.

## 📁 Contents
- **Key Files:**
  - `App.tsx` - Root component with routing and global state
  - `main.tsx` - React application entry point
  - `index.css` - Global styles and TailwindCSS imports
  - `vite-env.d.ts` - Vite environment type definitions

- **Directories:**
  - `components/` - Reusable UI components
  - `pages/` - Page-level components and routes
  - `services/` - API communication and external integrations
  - `contexts/` - React context providers for global state
  - `hooks/` - Custom React hooks
  - `types/` - TypeScript type definitions
  - `utils/` - Utility functions and helpers
  - `plugins/` - Plugin system components and utilities

## 🔧 Common Tasks
- **Create component**: Add to `components/` with TypeScript
- **Add new page**: Create in `pages/` and add to router
- **API integration**: Use or extend services in `services/`
- **Global state**: Add context in `contexts/`
- **Type definitions**: Define in `types/`

## 🔗 Dependencies
- Depends on: React, TypeScript, TailwindCSS, Vite
- Used by: Browser rendering, component hierarchy
- Integrates with: Backend API, plugin system, real-time messaging

## 💡 Quick Start for AI Agents
When working in this directory:
1. Follow React functional component patterns
2. Use TypeScript for all new code
3. Apply TailwindCSS classes for styling
4. Implement proper error boundaries
5. Use React Query for API state management

## ⚠️ Important Notes
- All components must be responsive
- Handle loading states and errors gracefully
- Plugin components are isolated and sandboxed
- Follow React best practices for performance