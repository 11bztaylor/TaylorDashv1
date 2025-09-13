# React Contexts

## 🎯 Purpose
React Context providers for global state management including authentication, theme, plugin state, and real-time data.

## 📁 Contents
- **Context Providers:**
  - AuthContext - User authentication and session management
  - ThemeContext - UI theme and appearance settings
  - PluginContext - Plugin state and configuration
  - WebSocketContext - Real-time messaging and updates
  - DashboardContext - Dashboard layout and widget state

## 🔧 Common Tasks
- **Use context**: Import useContext hook with specific context
- **Update state**: Use context actions and reducers
- **Provider setup**: Wrap components in context providers
- **State persistence**: Implement localStorage/sessionStorage
- **State validation**: Add TypeScript types for context state

## 🔗 Dependencies
- Depends on: React Context API, TypeScript, localStorage
- Used by: Components, pages, custom hooks
- Integrates with: Authentication, WebSocket, API services

## 💡 Quick Start for AI Agents
When working in this directory:
1. Define TypeScript interfaces for context state
2. Use useReducer for complex state management
3. Implement proper context provider hierarchy
4. Add error handling for context operations
5. Persist important state to localStorage

## ⚠️ Important Notes
- Avoid context overuse - use for truly global state
- Implement proper TypeScript typing
- Handle context value updates efficiently
- Plugin contexts are isolated for security