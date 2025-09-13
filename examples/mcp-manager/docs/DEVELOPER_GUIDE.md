# Developer Guide

## Component Architecture

### Adding New Server Types

Extend `MCPServer` interface in `App.tsx`:

```typescript
export interface MCPServer {
  id: string
  serverType?: 'homelab' | 'unifi' | 'unraid' | 'custom'
  capabilities?: string[]
  // existing fields...
}
```

### Custom Tool Handlers

Add tool-specific execution logic in `MCPToolsPanel.tsx`:

```typescript
const executeTool = async () => {
  // Custom tool handling
  switch (selectedTool.name) {
    case 'your_custom_tool':
      mockResult = await handleCustomTool(toolArgs)
      break
    // existing cases...
  }
}
```

### Server Discovery Extension

Modify discovery logic in `App.tsx`:

```typescript
const discoverServers = async () => {
  // Add custom discovery methods
  const configServers = await loadFromConfig()
  const networkServers = await scanNetwork()
  const customServers = await customDiscovery()
  
  setServers([...configServers, ...networkServers, ...customServers])
}
```

## Styling Customization

### Theme Colors
Primary colors defined in Tailwind CSS classes:
- **Primary**: `cyan-400`, `cyan-500`
- **Success**: `green-400`, `green-500`  
- **Error**: `red-400`, `red-500`
- **Warning**: `yellow-400`, `yellow-500`

### Status Color Mapping
```typescript
const getStatusColor = () => {
  switch (server.status) {
    case 'online': return 'border-green-500/30 bg-green-500/5'
    case 'offline': return 'border-red-500/30 bg-red-500/5'
    // Add custom status colors
  }
}
```

## API Integration

### Real MCP Server Connection

Replace mock data with actual MCP protocol calls:

```typescript
// Replace mock server discovery
const discoverServers = async () => {
  const response = await fetch('/api/mcp/servers')
  const servers = await response.json()
  setServers(servers)
}

// Replace mock tool execution
const executeTool = async () => {
  const response = await fetch('/api/mcp/execute', {
    method: 'POST',
    body: JSON.stringify({
      serverId: server.id,
      toolName: selectedTool.name,
      arguments: toolArgs
    })
  })
  const result = await response.json()
}
```

### Error Handling

Implement comprehensive error boundaries:

```typescript
const [error, setError] = useState<string | null>(null)

try {
  await executeTool()
} catch (err) {
  setError(err instanceof Error ? err.message : 'Unknown error')
}
```

## Component Extensions

### Custom Metrics Display

Extend `MCPServerCard` metrics:

```typescript
interface ServerMetrics {
  uptime: string
  requests: number
  errors: number
  // Add custom metrics
  avgResponseTime?: number
  lastToolExecution?: Date
  activeSessions?: number
}
```

### Additional Tool Types

Support complex tool schemas:

```typescript
const renderArgInput = (propName: string, schema: any) => {
  switch (schema.type) {
    case 'array':
      return <ArrayInput schema={schema} />
    case 'object':
      return <ObjectInput schema={schema} />
    // Handle complex types
  }
}
```

## Testing Patterns

### Component Testing
```typescript
import { render, fireEvent } from '@testing-library/react'
import { MCPServerCard } from './MCPServerCard'

test('server selection triggers callback', () => {
  const onSelect = jest.fn()
  render(<MCPServerCard server={mockServer} onSelect={onSelect} />)
  fireEvent.click(screen.getByText(mockServer.name))
  expect(onSelect).toHaveBeenCalled()
})
```

### Mock Data Generators
```typescript
export const createMockServer = (overrides = {}): MCPServer => ({
  id: 'test-server',
  name: 'Test Server',
  status: 'online',
  tools: [],
  ...overrides
})
```

## Performance Optimization

### Memoization
```typescript
const MemoizedServerCard = React.memo(MCPServerCard)
const toolList = useMemo(() => server.tools.filter(t => t.enabled), [server.tools])
```

### Virtual Scrolling
For large tool lists:
```typescript
import { FixedSizeList as List } from 'react-window'

const ToolsList = ({ tools }) => (
  <List height={400} itemCount={tools.length} itemSize={60}>
    {({ index, style }) => (
      <div style={style}>
        <ToolItem tool={tools[index]} />
      </div>
    )}
  </List>
)
```