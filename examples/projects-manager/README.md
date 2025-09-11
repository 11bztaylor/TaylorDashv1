# Projects Manager Plugin

A TaylorDash plugin for comprehensive project management with CRUD operations, status tracking, and real-time updates.

## Features

- **Project Creation**: Create new projects with metadata and status tracking
- **Project Management**: Full CRUD operations (Create, Read, Update, Delete)
- **Status Tracking**: Multiple project states (planning, active, on_hold, completed)
- **Real-time Updates**: Live updates through TaylorDash event system
- **Secure API Integration**: Built-in API key authentication for all backend calls
- **Responsive UI**: Clean, dark-themed interface with Tailwind CSS

## Architecture

This plugin follows the TaylorDash plugin architecture with:

- **Iframe Isolation**: Runs in isolated iframe for security
- **API Integration**: Communicates with TaylorDash backend via authenticated API calls
- **Event-Driven**: Publishes MQTT events for project lifecycle changes
- **Component-Based**: Modular React components for reusability

## Development

### Prerequisites
- Node.js 18+
- TaylorDash backend running with API key authentication

### Setup
```bash
cd examples/projects-manager
npm install
npm run dev
```

The plugin will start on port 5175 and proxy API calls to the TaylorDash backend.

### API Integration

The plugin uses the TaylorDash API with authentication:
- **Base URL**: `/api/v1/projects`
- **Authentication**: X-API-Key header with value `taylordash-dev-key`
- **Operations**: GET, POST, PUT, DELETE for full CRUD functionality

### Plugin Registration

The plugin is registered in the main TaylorDash application via:
```typescript
{
  id: "projects-manager",
  name: "Projects Manager", 
  kind: "ui",
  path: "/plugins/projects-manager",
  description: "Comprehensive project management with CRUD operations",
  version: "0.1.0",
  permissions: ["admin", "maintainer"]
}
```

## Security

- **API Key Authentication**: All backend requests include X-API-Key header
- **Iframe Sandboxing**: Plugin runs in isolated iframe environment
- **CORS Compliance**: Respects TaylorDash CORS policies
- **Input Validation**: Form validation and sanitization

## Integration

The plugin integrates with TaylorDash core systems:
- **Database**: Projects stored in PostgreSQL with proper schema
- **MQTT Events**: Publishes project lifecycle events to message bus
- **Observability**: Logs and metrics through TaylorDash infrastructure
- **Plugin Registry**: Managed through centralized plugin system

## Deployment

1. Build the plugin: `npm run build`
2. The built assets can be served by TaylorDash or external CDN
3. Plugin will be loaded via iframe at `/plugins/projects-manager`

## File Structure

```
src/
├── components/          # React components
│   ├── ProjectsList.tsx    # Project listing component
│   └── ProjectCreateModal.tsx  # Project creation modal
├── pages/              # Page components
│   └── ProjectsPage.tsx    # Main projects page
├── services/           # API services
│   └── api.ts             # API client with authentication
├── App.tsx            # Main application component
├── main.tsx           # Application entry point
└── index.css          # Global styles
```

## Version History

- **v0.1.0**: Initial release with full CRUD operations and API integration