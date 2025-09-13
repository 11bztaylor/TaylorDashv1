# Plugin System Components

## 🎯 Purpose
Frontend components and utilities for the plugin system including iframe sandboxing, plugin management UI, and security enforcement.

## 📁 Contents
- **Key Components:**
  - Plugin iframe wrapper with security sandboxing
  - Plugin manager interface for installation/configuration
  - Plugin card display and controls
  - Plugin API bridge for secure communication
  - Plugin validation and security components

## 🔧 Common Tasks
- **Render plugin**: Use sandboxed iframe component
- **Plugin communication**: Use secure message passing API
- **Manage plugins**: Install, enable, disable, configure
- **Security validation**: Check plugin permissions and capabilities
- **Plugin UI**: Create consistent plugin management interface

## 🔗 Dependencies
- Depends on: React, iframe sandboxing, plugin API services
- Used by: Dashboard, plugin pages, management interfaces
- Integrates with: Backend plugin system, security validation

## 💡 Quick Start for AI Agents
When working in this directory:
1. Always use sandboxed iframes for plugin content
2. Implement secure message passing for plugin communication
3. Validate all plugin operations for security
4. Handle plugin loading and error states
5. Follow consistent UI patterns for plugin management

## ⚠️ Important Notes
- All plugin content must be sandboxed
- Plugin communication requires security validation
- Handle malicious plugin attempts gracefully
- Implement proper CSP (Content Security Policy)