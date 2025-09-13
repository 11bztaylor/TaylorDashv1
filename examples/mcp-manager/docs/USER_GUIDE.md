# User Guide

## Interface Overview

### Network Status Dashboard
**Health Percentage** - Overall network health (online servers / total servers)
**Status Cards** - Online, offline, and issue counts with color coding
**Health Bar** - Visual progress indicator for system health

### Server Management

#### Server Cards
- **Status Indicators**: Green (online), red (offline), yellow (connecting/error)
- **Server Details**: Name, description, host address, tool count
- **Metrics Display**: Uptime, request counts, error tracking
- **Refresh Button**: Manual server status refresh

#### Server Selection
Click any server card to view details and available tools.

### Tool Execution

#### Available Tools Panel
- **Tool List**: Shows all tools available from selected server
- **Tool Details**: Name, description, last execution time
- **Selection**: Click to select tool for execution

#### Tool Execution Interface
```
Parameters: Dynamic form based on tool schema
Required fields marked with red asterisk (*)
Execute Button: Runs tool with current parameters
```

#### Execution History
- **Chronological List**: Most recent executions first
- **Full Details**: Arguments, results, errors, timestamps
- **Result Display**: Formatted output with syntax highlighting

## Common Workflows

### Server Health Monitoring
1. View Network Status dashboard for overall health
2. Check individual server status indicators
3. Use refresh buttons to update connection status

### Tool Discovery
1. Select server from server list
2. Browse Available Tools panel
3. Review tool descriptions and requirements

### Tool Execution
1. Select target tool from tools panel
2. Fill required parameters in form
3. Click "Execute Tool" button
4. Monitor results in execution history

### Network Troubleshooting
1. Check Network Status for offline servers
2. Use server refresh to test connectivity
3. Review execution history for error patterns

## Status Indicators

**Green**: Server online and responding
**Red**: Server offline or unreachable  
**Yellow**: Connection issues or errors
**Spinning Icon**: Connection attempt in progress

## Tool Parameter Types

**String**: Text input for commands, hostnames, descriptions
**Number**: Numeric input for counts, timeouts, port numbers
**Boolean**: Checkbox for true/false options