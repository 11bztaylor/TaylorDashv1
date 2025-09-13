# Security Guide

## Authentication Model

### TaylorDash Integration
- **Session Inheritance**: Plugin inherits TaylorDash user authentication
- **RBAC Enforcement**: Admin-only access via permission system
- **Session Validation**: Automatic session timeout handling

### Permission Requirements
```typescript
// Plugin registry configuration
permissions: ["admin"]  // Only admin users can access plugin
```

## Iframe Security

### Sandbox Configuration
```typescript
sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
```

**Security Boundaries:**
- **allow-scripts**: Enable JavaScript execution within plugin
- **allow-same-origin**: Required for TaylorDash session inheritance  
- **allow-forms**: Enable tool parameter input forms
- **allow-popups**: Support for external tool documentation

### Content Security Policy
Plugin serves from isolated localhost:5174 port with restricted permissions.

## Input Validation

### Tool Parameter Validation
```typescript
// Schema-based validation
const validateArgs = (args: Record<string, any>, schema: any) => {
  const required = schema.required || []
  for (const field of required) {
    if (!args[field]) throw new Error(`${field} is required`)
  }
}
```

### Command Injection Prevention
- **Type Enforcement**: TypeScript ensures type safety
- **Schema Validation**: All tool parameters validated against MCP schemas
- **Sanitization**: Input sanitization for string parameters

## Network Security

### MCP Server Communication
- **Local Network Only**: Default configuration scans local network
- **Authentication Headers**: MCP protocol authentication support
- **TLS Encryption**: HTTPS support for secure MCP connections

### Cross-Origin Handling
```typescript
// Restricted to local development
const MCPServers = [
  { host: 'localhost:8080' },
  { host: 'localhost:8081' },
  { host: 'unraid.local:8082' }
]
```

## Error Handling

### Sensitive Data Protection
```typescript
// Error sanitization
const sanitizeError = (error: Error): string => {
  // Remove sensitive paths, credentials
  return error.message.replace(/\/[^\/\s]+\/[^\/\s]+/g, '[PATH]')
}
```

### Execution Result Filtering
- **Command Output**: Filter sensitive information from tool results
- **Error Messages**: Sanitize error messages before display
- **Logging**: No sensitive data in browser console

## Best Practices

### Plugin Development
1. **Input Validation**: Always validate user inputs
2. **Error Boundaries**: Implement comprehensive error handling
3. **Session Management**: Respect TaylorDash session lifecycle
4. **Network Restrictions**: Limit network access to required endpoints

### Deployment Security  
1. **Admin Access**: Ensure plugin remains admin-restricted
2. **Network Isolation**: Deploy on isolated network segments
3. **Regular Updates**: Keep dependencies updated for security patches
4. **Audit Logs**: Monitor tool execution for security events

## Security Monitoring

### Execution Tracking
All tool executions logged with:
- **User Identity**: From TaylorDash session
- **Timestamp**: Execution time
- **Parameters**: Tool arguments (sanitized)
- **Results**: Success/failure status

### Access Control
- **Role Verification**: Permission checks on every plugin load
- **Session Validation**: Continuous authentication state monitoring
- **Audit Trail**: Complete record of user actions within plugin