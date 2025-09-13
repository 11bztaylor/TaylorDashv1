# MCP Manager Documentation

Complete technical documentation for the MCP Manager plugin for TaylorDash.

## Overview

MCP Manager provides comprehensive Model Context Protocol server management through a modern React interface integrated with TaylorDash's plugin ecosystem.

**Key Capabilities:**
- Real-time MCP server monitoring and status tracking
- Interactive tool discovery and execution interface  
- Network health visualization and metrics dashboard
- Admin-controlled access with TaylorDash RBAC integration

## Documentation Structure

### [Architecture Guide](./ARCHITECTURE.md)
System design, component interactions, data flow patterns, and integration points with TaylorDash.

### [Installation Guide](./INSTALLATION.md) 
Step-by-step setup instructions, dependencies, build configuration, and TaylorDash integration.

### [User Guide](./USER_GUIDE.md)
Interface walkthrough, feature usage, common workflows, and status indicators.

### [Developer Guide](./DEVELOPER_GUIDE.md)
Component extension, API integration, custom tool handlers, and testing patterns.

### [Security Guide](./SECURITY.md)
Authentication model, iframe security, input validation, and network security considerations.

### [Troubleshooting Guide](./TROUBLESHOOTING.md)
Common issues, solutions, debug procedures, and performance optimization.

## Quick Start

```bash
# Install and run
cd /TaylorProjects/TaylorDashv1/examples/mcp-manager
npm install && npm run dev

# Access plugin
# Navigate to TaylorDash → Plugins → MCP Manager
```

## Technical Specifications

**Frontend**: React 18 + TypeScript + Vite development server
**Integration**: Iframe-based TaylorDash plugin with admin permissions
**Protocol Support**: Model Context Protocol for homelab automation
**Security**: Sandboxed execution with session inheritance

## Production Readiness

- **Component Architecture**: Modular, testable React components
- **Type Safety**: Complete TypeScript implementation  
- **Error Handling**: Comprehensive error boundaries and validation
- **Security Model**: Admin-only access with input sanitization
- **Performance**: Optimized rendering and state management

The MCP Manager demonstrates production-quality plugin development for the TaylorDash ecosystem.