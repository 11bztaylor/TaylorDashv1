# Frontend

## 🎯 Purpose
React-based frontend providing dynamic dashboard interface, plugin system UI, and real-time data visualization for TaylorDash.

## 📁 Contents
- **Key Files:**
  - `src/App.tsx` - Main application component with routing
  - `package.json` - Dependencies and build scripts
  - `vite.config.ts` - Vite bundler configuration
  - `tailwind.config.js` - TailwindCSS styling configuration
  - `tsconfig.json` - TypeScript configuration

- **Directories:**
  - `src/` - All source code including components, pages, services
  - `node_modules/` - NPM package dependencies
  - `.vite/` - Vite build cache and artifacts

## 🔧 Common Tasks
- **Start development**: `npm run dev`
- **Build for production**: `npm run build`
- **Run linting**: `npm run lint`
- **Install packages**: `npm install [package-name]`
- **Type checking**: `npm run type-check`

## 🌍 Remote Access (No localhost)

When you open the UI from another machine, configure the API/plugin origins:

- Set `VITE_API_ORIGIN` to your backend origin (e.g., `http://SERVER_IP:8000` or `https://dash.local`).
- If plugin UIs run on separate ports/hosts, set `VITE_PLUGIN_ORIGIN` or per‑plugin overrides:
  - `VITE_PLUGIN_MCP_MANAGER`, `VITE_PLUGIN_MIDNIGHT_HUD`, `VITE_PLUGIN_PROJECTS_MANAGER`.

Example `.env` (dev):
```ini
VITE_API_ORIGIN=http://127.0.0.1:8000
VITE_PLUGIN_ORIGIN=http://127.0.0.1
# VITE_PLUGIN_MIDNIGHT_HUD=http://127.0.0.1:5173
```

The app automatically attaches the session token to API requests; debug logs are shown only in development.

## 🔗 Dependencies
- Depends on: Backend API, WebSocket connections
- Used by: End users, plugin interfaces
- Integrates with: Real-time messaging, authentication system

## 💡 Quick Start for AI Agents
When working in this directory:
1. Check `src/App.tsx` for overall application structure
2. Review `src/components/` for reusable UI components
3. Use `src/services/` for API integration patterns
4. Follow TypeScript types in `src/types/`
5. Use TailwindCSS for consistent styling

## ⚠️ Important Notes
- All API calls go through service layer
- Components must handle loading and error states
- Plugin iframes are sandboxed for security
- Real-time updates use WebSocket connections
