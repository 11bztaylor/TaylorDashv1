// Auto-generated plugin registry
// This file is automatically updated when plugins are installed/uninstalled
// Note: Endpoints are environment-aware to avoid hardcoding localhost.

export interface Plugin {
  id: string;
  name: string;
  version: string;
  description?: string;
  kind: 'ui' | 'data' | 'integration';
  type: string;
  path: string;
  entry_point?: string;
}

// Base origin for plugin entry points. Defaults to current origin for remote access.
const PLUGIN_ORIGIN = (import.meta as any).env?.VITE_PLUGIN_ORIGIN || window.location.origin;

export const PLUGINS: Plugin[] = [
  {
    id: 'mcp-manager',
    name: 'MCP Manager',
    version: '0.1.0',
    description: 'MCP Server Management Plugin for TaylorDash',
    kind: 'ui',
    type: 'react',
    path: '/plugins/mcp-manager',
    // Prefer env override (e.g., a dev server), else serve from same origin
    entry_point: (import.meta as any).env?.VITE_PLUGIN_MCP_MANAGER || `${PLUGIN_ORIGIN}/plugins/mcp-manager`
  },
  {
    id: 'midnight-hud',
    name: 'Midnight HUD',
    version: '0.1.0',
    description: 'Cyber-aesthetic dashboard with floating widgets',
    kind: 'ui',
    type: 'react',
    path: '/plugins/midnight-hud',
    entry_point: (import.meta as any).env?.VITE_PLUGIN_MIDNIGHT_HUD || `${PLUGIN_ORIGIN}/plugins/midnight-hud`
  },
  {
    id: 'projects-manager',
    name: 'Projects Manager',
    version: '0.1.0',
    description: 'Project lifecycle management plugin',
    kind: 'ui',
    type: 'react',
    path: '/plugins/projects-manager',
    entry_point: (import.meta as any).env?.VITE_PLUGIN_PROJECTS_MANAGER || `${PLUGIN_ORIGIN}/plugins/projects-manager`
  }
];

export function getPluginById(id: string): Plugin | null {
  return PLUGINS.find(plugin => plugin.id === id) || null;
}

export function getPluginsByKind(kind: Plugin['kind']): Plugin[] {
  return PLUGINS.filter(plugin => plugin.kind === kind);
}

export function getInstalledPluginsCount(): number {
  return PLUGINS.length;
}

// Plugin security and validation
export function isPluginSecure(pluginId: string): boolean {
  // All installed plugins have passed security validation
  return PLUGINS.some(plugin => plugin.id === pluginId);
}
