# MCP Manager Architecture

Complete Model Context Protocol server management interface for TaylorDash.

## System Architecture

**Frontend**: React 18 + TypeScript + Vite development server
**Integration**: TaylorDash plugin system with iframe embedding
**Protocol**: Model Context Protocol for server communication

## Core Components

### App.tsx - Main Application Controller
- **Server Discovery**: Auto-detects MCP servers on network
- **State Management**: Manages server list and selection state
- **Connection Monitoring**: Real-time status updates and health checks

```typescript
interface MCPServer {
  id: string
  name: string
  status: 'online' | 'offline' | 'connecting' | 'error'
  host: string
  tools: MCPTool[]
  metrics?: ServerMetrics
}
```

### MCPServerCard - Individual Server Display
- **Status Visualization**: Color-coded connection states
- **Metrics Dashboard**: Uptime, request counts, error tracking
- **Interactive Controls**: Server refresh and selection handling

### MCPConnectionStatus - Network Overview
- **Health Metrics**: System-wide network health percentage
- **Status Aggregation**: Online/offline/error server counts
- **Visual Indicators**: Color-coded status cards and progress bar

### MCPToolsPanel - Tool Execution Interface
- **Schema Validation**: Dynamic form generation from tool schemas
- **Parameter Input**: Type-safe input handling with validation
- **Execution History**: Chronological tool execution tracking

## Data Flow

```
Network Discovery → Server Registration → Tool Introspection → User Interaction
      ↓                     ↓                    ↓                  ↓
  Auto-detect MCP    Store server state   Query available    Execute tools
  servers on ports   with connection      tools and their    with parameter
  and configuration  status monitoring    input schemas      validation
```

## Integration Points

### TaylorDash Plugin System
- **Registry Entry**: `/frontend/src/plugins/registry.ts`
- **Route Handler**: `/frontend/src/pages/plugins/MCPManagerPage.tsx`
- **Iframe Embedding**: Sandboxed execution at `localhost:5174`

### Authentication Flow
- **Session Inheritance**: Inherits TaylorDash user session
- **RBAC Integration**: Admin-only access through permission system
- **Security Boundaries**: Iframe sandbox with controlled permissions

## Component Interactions

**App** manages global state and orchestrates child components
**ServerCard** handles individual server display and user interactions
**ConnectionStatus** aggregates and visualizes overall system health
**ToolsPanel** provides interactive tool execution interface

Each component maintains focused responsibilities with clear data flow patterns.