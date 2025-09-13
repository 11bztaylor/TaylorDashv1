# Custom React Hooks

## 🎯 Purpose
Reusable custom hooks for state management, API integration, real-time data, and common UI patterns.

## 📁 Contents
- **Hook Categories:**
  - API hooks (useAuth, usePlugins, useDashboard)
  - WebSocket hooks (useWebSocket, useRealTimeData)
  - UI hooks (useLocalStorage, useTheme, useModal)
  - Plugin hooks (usePluginState, usePluginAPI)
  - Utility hooks (useDebounce, useAsync, useInterval)

## 🔧 Common Tasks
- **Create custom hook**: Use use prefix, follow React rules
- **State management**: Use useState, useReducer, useContext
- **Side effects**: Use useEffect for API calls, subscriptions
- **Performance**: Use useMemo, useCallback for optimization
- **Cleanup**: Implement proper cleanup in useEffect

## 🔗 Dependencies
- Depends on: React hooks, TypeScript, API services, contexts
- Used by: Components, pages, other hooks
- Integrates with: State management, API layer, real-time updates

## 💡 Quick Start for AI Agents
When working in this directory:
1. Follow React hooks rules and best practices
2. Add proper TypeScript types for hook parameters and returns
3. Implement error handling and loading states
4. Use dependency arrays correctly in useEffect
5. Abstract common patterns into reusable hooks

## ⚠️ Important Notes
- Follow rules of hooks (no conditional calls)
- Implement proper cleanup to prevent memory leaks
- Plugin hooks must handle security restrictions
- Use React Query hooks for server state management