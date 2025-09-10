# Multi-View & Tabs System

TaylorDash implements a flexible multi-view interface with tabbed navigation, allowing users to organize different aspects of their project monitoring and management workflows.

## View Architecture

### Core Views
- **Dashboard**: Main operational overview with real-time metrics
- **Projects**: Project-specific monitoring and management interface  
- **Analytics**: Data analysis and reporting views
- **Settings**: Configuration and preferences

### Plugin Views
TaylorDash supports extensible plugin-based views for custom functionality:

- **[Midnight HUD](ui/midnight-hud.md)**: Cyber-aesthetic dashboard plugin demonstrating visual-first workflow
- **Custom Dashboards**: User-defined monitoring interfaces
- **Third-party Integrations**: External service dashboards

## Tab Management

### Dynamic Tabs
- **Add/Remove**: Users can dynamically add and remove tabs
- **Reordering**: Drag-and-drop tab reordering
- **Persistence**: Tab state preserved across sessions
- **Context**: Each tab maintains independent state and context

### Tab Types
1. **Static Tabs**: Core application views (Dashboard, Projects)
2. **Dynamic Tabs**: User-created or plugin-generated views  
3. **Modal Tabs**: Temporary views for specific tasks
4. **Plugin Tabs**: Embedded plugin interfaces

## View State Management

### State Isolation
Each view maintains independent state to prevent cross-contamination:
- **Local State**: View-specific component state
- **Context State**: Shared state within view scope
- **Global State**: Application-wide state (user, theme, etc.)

### Persistence Strategy
- **Session Storage**: Temporary view state during session
- **Local Storage**: Persistent view preferences and layouts
- **Backend Sync**: Critical state synchronized with server

## Navigation Patterns

### Primary Navigation
- **Top-level Tabs**: Main application sections
- **Breadcrumbs**: Hierarchical navigation within complex views
- **Sidebar**: Contextual navigation for active view

### Secondary Navigation  
- **Sub-tabs**: Within-view section navigation
- **Quick Actions**: Common tasks accessible from any view
- **Search**: Global search across all views and content

## Plugin Integration

### Plugin View Registration
See [Plugin System Documentation](plugins.md) for detailed integration patterns:

```typescript
// Register plugin view in tab system
const pluginViews = PLUGINS.filter(p => p.kind === 'ui').map(plugin => ({
  id: plugin.id,
  name: plugin.name,
  path: plugin.path,
  component: () => <PluginView plugin={plugin} />
}));
```

### Cross-View Communication
- **Event Bus**: MQTT-based messaging between views
- **Shared Context**: React context for related view state
- **URL State**: Shareable view state via URL parameters

## Responsive Design

### Breakpoint Strategy
- **Desktop**: Full multi-tab interface with sidebar
- **Tablet**: Collapsed sidebar, full tab functionality
- **Mobile**: Bottom tab bar, single view focus

### Layout Adaptation
- **Grid Layouts**: Responsive grid systems for content
- **Flexible Widgets**: Resizable and repositionable components
- **Progressive Disclosure**: Hide complexity on smaller screens

## Accessibility

### Keyboard Navigation
- **Tab Focus**: Logical tab order through interface
- **Keyboard Shortcuts**: Quick view switching (Ctrl+1, Ctrl+2, etc.)
- **Screen Reader**: Proper ARIA labels and navigation landmarks

### Visual Accessibility
- **High Contrast**: Support for high contrast themes
- **Font Scaling**: Responsive to user font size preferences
- **Color Independence**: Information not conveyed by color alone

## Performance Considerations

### Lazy Loading
- **View Components**: Load view content on demand
- **Plugin Views**: Lazy load plugin interfaces
- **Heavy Components**: Defer expensive component loading

### Memory Management
- **View Cleanup**: Unmount inactive views after timeout
- **State Cleanup**: Clear unnecessary state on view switch
- **Resource Management**: Release resources when views close

## Future Enhancements

### Advanced Features
- **Multi-Panel Views**: Split-screen view layouts
- **Floating Windows**: Detachable view windows
- **View Templates**: Predefined view configurations
- **Collaborative Views**: Shared view state between users

### User Experience
- **View Workspaces**: Save and restore view layouts
- **Smart Tabs**: AI-suggested tab organization
- **Context Switching**: Automatic view switching based on activity
- **View History**: Navigation history and quick switching

---

The multi-view system provides a flexible foundation for organizing complex operational workflows while maintaining performance and user experience quality.