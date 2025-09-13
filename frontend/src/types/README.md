# TypeScript Types

## 🎯 Purpose
Centralized TypeScript type definitions for API responses, component props, plugin interfaces, and application state.

## 📁 Contents
- **Type Categories:**
  - API types (User, Plugin, Dashboard, Response formats)
  - Component prop types and interfaces
  - Plugin system types and plugin API interfaces
  - Global application state types
  - Utility types and generic helpers

## 🔧 Common Tasks
- **Define new type**: Create interface or type alias
- **API response types**: Match backend response structures
- **Component props**: Define interfaces for component properties
- **Plugin types**: Define plugin configuration and state types
- **Generic types**: Create reusable type utilities

## 🔗 Dependencies
- Depends on: TypeScript, API contract definitions
- Used by: All TypeScript files, components, services, hooks
- Integrates with: Backend API types, plugin system contracts

## 💡 Quick Start for AI Agents
When working in this directory:
1. Keep types synchronized with backend API contracts
2. Use descriptive names and comprehensive documentation
3. Prefer interfaces over types for extensibility
4. Export types from index files for easy importing
5. Use utility types (Partial, Pick, Omit) for variations

## ⚠️ Important Notes
- Types must match backend API exactly
- Plugin types require security constraint definitions
- Use strict TypeScript configuration
- Avoid any type - define proper interfaces