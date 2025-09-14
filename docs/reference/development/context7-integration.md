# Context7 MCP Integration Guide

## Overview

Context7 MCP is now integrated into the TaylorDash development environment, providing enhanced context management and code understanding capabilities for Claude Code sessions.

## Installation Status

✅ **Installed**: Context7 MCP v1.0.17 globally installed
✅ **Configured**: Added to Claude Code MCP configuration
✅ **Validated**: Integration tested and working

## Available Tools

### `mcp__context7__resolve-library-id`
- **Purpose**: Resolve library names to unique identifiers
- **Usage**: When you need to identify specific libraries or frameworks
- **When to use**: Starting new features, analyzing dependencies, code reviews

### `mcp__context7__get-library-docs`
- **Purpose**: Fetch comprehensive library documentation
- **Usage**: Get detailed documentation for libraries in your project
- **When to use**: Implementation tasks, troubleshooting, API integration

## When to Use Context7

### 🎯 **Primary Use Cases**

1. **New Feature Implementation**
   - Understanding unfamiliar libraries in the codebase
   - Getting API documentation for external services
   - Learning framework-specific patterns

2. **Code Review & Analysis**
   - Validating library usage patterns
   - Understanding complex dependencies
   - Documenting technical decisions

3. **Troubleshooting & Debugging**
   - Understanding library behavior
   - Finding correct API usage
   - Resolving compatibility issues

4. **Architecture Decisions**
   - Evaluating library alternatives
   - Understanding framework capabilities
   - Planning integrations

### 🚫 **When NOT to Use Context7**

- Simple file operations (use standard tools)
- Basic code writing (Context7 is for understanding, not generation)
- Project-specific business logic (Context7 is for external libraries)

## Integration with TaylorDash Agents

### Compatible Agents
Context7 works well with these TaylorDash agents:

- **`backend_dev`**: Use Context7 to understand FastAPI, SQLAlchemy, Pydantic patterns
- **`frontend_dev`**: Get React, TypeScript, Vite documentation
- **`architecture_contracts`**: Understand OpenAPI and schema validation libraries
- **`observability`**: Learn Prometheus, Grafana, OpenTelemetry integration
- **`security_rbac`**: Research authentication libraries and security patterns

### Workflow Integration

```
1. Agent identifies unknown library/framework
2. Use Context7 to resolve library ID
3. Fetch comprehensive documentation
4. Apply knowledge to implementation
5. Document decisions in ADRs
```

## Best Practices

### ✅ **Do**
- Use Context7 when encountering unfamiliar libraries
- Fetch docs before making architectural decisions
- Document Context7 findings in commit messages
- Share Context7 insights with team in PRs

### ❌ **Don't**
- Use Context7 for every small task
- Fetch docs for well-known libraries you understand
- Replace proper testing with Context7 research
- Use Context7 instead of official documentation when available

## Configuration Details

**Location**: `/home/zach/home-ops/claude-desktop-config.json`

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["@upstash/context7-mcp"],
      "description": "Context7 MCP - Enhanced development context management and code understanding"
    }
  }
}
```

## Examples

### Example 1: New Library Research
```
Scenario: Need to implement WebSocket connections in FastAPI backend
1. Use Context7 to resolve "fastapi-websockets" library ID
2. Fetch documentation for WebSocket patterns
3. Apply knowledge to implement real-time features
```

### Example 2: Frontend Framework Update
```
Scenario: Upgrading React components to use newer patterns
1. Use Context7 to get latest React documentation
2. Understand new hook patterns and best practices
3. Implement updates following documented patterns
```

### Example 3: Security Implementation
```
Scenario: Adding JWT authentication to API
1. Use Context7 to research JWT library options
2. Fetch security best practices documentation
3. Implement secure authentication following guidelines
```

## Troubleshooting

### Context7 Not Available
```bash
# Verify installation
npm list -g @upstash/context7-mcp

# Reinstall if needed
npm install -g @upstash/context7-mcp@latest
```

### MCP Connection Issues
1. Check Claude Code MCP server status
2. Verify configuration in claude-desktop-config.json
3. Restart Claude Code if needed

## Contributing

When using Context7 in TaylorDash development:

1. **Document Usage**: Note Context7 usage in commit messages
2. **Share Insights**: Include Context7 findings in PR descriptions
3. **Update Docs**: Add Context7 discoveries to project documentation
4. **Agent Integration**: Consider how Context7 enhances agent workflows

## Support

- **Context7 Issues**: https://github.com/upstash/context7-mcp
- **Claude Code MCP**: https://docs.anthropic.com/en/docs/claude-code
- **TaylorDash Integration**: See project maintainers

---

*Last Updated: 2025-09-13*
*Integration Status: ✅ Active*
*Version: Context7 MCP v1.0.17*