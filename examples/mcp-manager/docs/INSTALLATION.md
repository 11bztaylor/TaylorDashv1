# Installation Guide

## Prerequisites

- Node.js 18+ with npm
- TaylorDash development environment
- Admin permissions in TaylorDash

## Quick Start

```bash
cd /TaylorProjects/TaylorDashv1/examples/mcp-manager
npm install
npm run dev
```

Plugin available at `http://localhost:5174`

## TaylorDash Integration

### 1. Plugin Registration
Plugin automatically registered in `/frontend/src/plugins/registry.ts`:

```typescript
{
  id: "mcp-manager",
  name: "MCP Manager", 
  kind: "integration",
  path: "/plugins/mcp-manager",
  permissions: ["admin"]
}
```

### 2. Route Configuration
Access via TaylorDash navigation: **Plugins → MCP Manager**

### 3. Development Server
```bash
# Start plugin development server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Production build
npm run build
```

## Dependencies

**Core Runtime:**
- React 18.2.0 - UI framework
- TypeScript 5.2.2 - Type safety
- Vite 5.0.8 - Development server

**UI Components:**
- lucide-react 0.263.1 - Icon library
- clsx 2.0.0 - Conditional styling

## Plugin Configuration

### Port Configuration
Default: `http://localhost:5174`

Update in `vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    port: 5174
  }
})
```

### Security Settings
Iframe sandbox permissions in `MCPManagerPage.tsx`:
```typescript
sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
```

## Build Process

```bash
# Development with hot reload
npm run dev

# Production build
npm run build
# Creates /dist folder with optimized assets

# Preview production build
npm run preview
```

Build output serves static files for production deployment.