# Midnight HUD - TaylorDash Plugin Example

A cyber-aesthetic dashboard demonstrating TaylorDash's visual-first workflow capabilities.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Features

- **Drag & Drop Widgets**: Freely position dashboard components
- **Persistent State**: Layout saves across sessions
- **Multi-View Navigation**: Switch between Home and Library views
- **Real-time Simulation**: Mock system metrics and project data
- **Cyber Aesthetic**: Glass morphism with TaylorDash branding

## Integration

This example integrates with TaylorDash via:
- Plugin route: `/plugins/midnight-hud`
- Iframe embedding for isolation
- RBAC-compliant viewer access
- Brand-consistent styling

## Architecture

- React 18 + TypeScript + Vite
- Tailwind CSS with custom theme
- React DnD for interactions
- localStorage for persistence