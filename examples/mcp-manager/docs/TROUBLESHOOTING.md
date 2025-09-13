# Troubleshooting Guide

## Common Issues

### Plugin Not Loading

**Symptom**: Plugin shows loading screen indefinitely
**Causes**: 
- Development server not running
- Port 5174 blocked or in use
- Network connectivity issues

**Solutions**:
```bash
# Check if development server is running
npm run dev

# Verify port availability
netstat -tulpn | grep :5174

# Test direct access
curl http://localhost:5174
```

### Server Discovery Problems

**Symptom**: No MCP servers found or servers show offline
**Causes**:
- MCP servers not running
- Network connectivity issues
- Firewall blocking connections

**Solutions**:
1. **Verify MCP Server Status**:
```bash
# Check if MCP server is running
curl http://localhost:8080/health

# Test network connectivity
ping localhost
```

2. **Check Firewall Settings**:
```bash
# Allow MCP ports through firewall
sudo ufw allow 8080:8085/tcp
```

### Tool Execution Failures

**Symptom**: Tools fail to execute or return errors
**Common Errors**:
- "Connection refused"
- "Tool not found" 
- "Parameter validation failed"

**Solutions**:
1. **Parameter Validation**:
   - Ensure all required parameters filled
   - Check parameter types match schema
   - Verify parameter formats (e.g., valid hostnames)

2. **Server Connectivity**:
   - Refresh server status
   - Check server logs for errors
   - Verify MCP server is responding

### Performance Issues

**Symptom**: Slow loading or unresponsive interface
**Causes**:
- Too many servers being monitored
- Large execution history
- Memory leaks in React components

**Solutions**:
```bash
# Clear browser cache and reload
# Monitor memory usage in browser dev tools
# Reduce polling frequency for server status
```

## Development Issues

### TypeScript Compilation Errors

```bash
# Clear TypeScript cache
rm -rf node_modules/.cache
npm run type-check
```

### Hot Reload Not Working

```bash
# Restart development server
npm run dev

# Clear Vite cache
rm -rf node_modules/.vite
```

### Component State Issues

**Problem**: State not updating correctly
**Solution**: Check React DevTools for state mutations

## Network Configuration

### MCP Server Discovery

Default discovery attempts these endpoints:
- `localhost:8080` - Home Lab MCP
- `localhost:8081` - UniFi Network MCP  
- `unraid.local:8082` - Unraid MCP

**Custom Configuration**:
```typescript
// Update server list in App.tsx
const customServers = [
  { host: 'your-server:8090' },
  // Add your MCP servers
]
```

### Proxy Configuration

For production deployment behind reverse proxy:

```nginx
# nginx configuration
location /plugins/mcp-manager {
    proxy_pass http://localhost:5174;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## Browser Compatibility

### Iframe Sandbox Issues

**Chrome**: Ensure `allow-same-origin` in sandbox attribute
**Firefox**: Check Content Security Policy headers
**Safari**: Verify cross-origin permissions

### JavaScript Errors

Check browser console for:
- CORS violations
- Uncaught exceptions
- Network request failures

## Debug Mode

### Enable Verbose Logging

```typescript
// Add to App.tsx
const DEBUG = true
if (DEBUG) {
  console.log('Server discovery:', servers)
  console.log('Tool execution:', execution)
}
```

### Network Request Monitoring

1. Open browser Developer Tools
2. Navigate to Network tab
3. Monitor MCP server requests
4. Check for failed requests or timeouts

## Getting Help

### Log Collection

Before reporting issues:
```bash
# Collect development logs
npm run dev 2>&1 | tee mcp-manager.log

# Include browser console output
# Include network requests from dev tools
```

### Issue Reporting

Include:
- Browser version and OS
- TaylorDash version
- Plugin version 
- Complete error messages
- Steps to reproduce

### Common Solutions Summary

1. **Plugin won't load**: Check dev server and port 5174
2. **No servers found**: Verify MCP servers running on expected ports  
3. **Tools don't work**: Check parameter validation and server connectivity
4. **Performance issues**: Monitor memory usage and reduce polling frequency
5. **Build errors**: Clear caches and reinstall dependencies