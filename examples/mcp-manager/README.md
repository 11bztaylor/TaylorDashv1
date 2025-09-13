# MCP Manager Plugin for TaylorDash

A comprehensive Model Context Protocol (MCP) server management interface for TaylorDash.

## Features

- **Real-time Server Monitoring**: Track the status of multiple MCP servers
- **Tool Discovery**: Automatically discover and list available tools from each MCP server
- **Interactive Tool Execution**: Execute MCP tools with parameter validation and result display
- **Connection Health Dashboard**: Overview of network health and server status
- **Execution History**: Track recent tool executions with timestamps and results
- **Responsive Design**: Optimized for both desktop and tablet interfaces

## MCP Server Support

This plugin is designed to work with any compliant MCP server, including:

- **Home Lab MCP**: Infrastructure management and monitoring
- **UniFi Network MCP**: Network device and client management
- **Unraid MCP**: Server management and container orchestration
- Custom MCP servers following the Model Context Protocol specification

## Architecture

### Components

- **MCPServerCard**: Individual server status and metrics display
- **MCPConnectionStatus**: Network overview and health indicators  
- **MCPToolsPanel**: Tool discovery, parameter input, and execution interface

### Data Flow

1. **Server Discovery**: Automatically detects available MCP servers on the network
2. **Status Monitoring**: Periodic health checks and connection status updates
3. **Tool Introspection**: Queries server capabilities and available tools
4. **Interactive Execution**: Real-time tool execution with parameter validation

## Development

### Prerequisites

- Node.js 18+ 
- npm or yarn
- TaylorDash development environment

### Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint
```

The plugin will be available at `http://localhost:5174` for iframe embedding in TaylorDash.

### Integration with TaylorDash

1. **Register Plugin**: Add to `frontend/src/plugins/registry.ts`
2. **Route Configuration**: Create route handler in TaylorDash
3. **Permission Setup**: Configure RBAC permissions for plugin access
4. **Authentication**: Ensure plugin respects TaylorDash user sessions

## Plugin Configuration

### Permissions

- **viewer**: Read-only access to server status and tool listings
- **admin**: Full access including tool execution and server management

### Security

- **Iframe Sandboxing**: Runs in sandboxed iframe for security isolation
- **RBAC Integration**: Respects TaylorDash role-based access controls
- **Session Authentication**: Integrates with TaylorDash user authentication

## MCP Server Integration

### Supported Operations

- **List Tools**: Discover available tools and their schemas
- **Execute Tools**: Run tools with parameter validation
- **Server Status**: Monitor connection health and availability
- **Metrics Collection**: Gather server performance data

### Network Discovery

The plugin automatically discovers MCP servers through:

- **Local Network Scanning**: Discovers servers on common ports
- **Configuration Files**: Reads server definitions from config
- **Manual Addition**: Allow users to add servers manually

## Styling

The plugin follows TaylorDash design conventions:

- **Dark Theme**: Consistent with TaylorDash's dark aesthetic
- **Cyan Accents**: Primary brand color for highlights and actions
- **Responsive Grid**: Adapts to different screen sizes and orientations
- **Status Indicators**: Color-coded status with clear visual hierarchy

## Error Handling

- **Network Failures**: Graceful degradation when servers are unreachable
- **Tool Execution Errors**: Clear error messages and retry mechanisms
- **Validation**: Input validation before tool execution
- **Loading States**: Clear indication of ongoing operations

## Future Enhancements

- **Plugin Marketplace Integration**: Install/manage plugins through MCP servers
- **Advanced Filtering**: Search and filter tools by category or function
- **Scheduled Execution**: Set up automated tool execution schedules  
- **Alert System**: Notifications for server status changes
- **Batch Operations**: Execute tools across multiple servers simultaneously

---

Built for TaylorDash Plugin Ecosystem v0.1.0