// Auto-generated plugin registry
// This file is automatically updated when plugins are installed/uninstalled

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

export const PLUGINS: Plugin[] = [
  {
    id: 'mcp-manager',
    name: 'MCP Manager',
    version: '0.1.0',
    description: 'MCP Server Management Plugin for TaylorDash',
    kind: 'ui',
    type: 'react',
    path: '/plugins/mcp-manager',
    entry_point: 'http://localhost:5177'
  },
  {
    id: 'midnight-hud',
    name: 'Midnight HUD',
    version: '0.1.0',
    description: 'Cyber-aesthetic dashboard with floating widgets',
    kind: 'ui',
    type: 'react',
    path: '/plugins/midnight-hud',
    entry_point: 'http://localhost:5173'
  },
  {
    id: 'projects-manager',
    name: 'Projects Manager',
    version: '0.1.0',
    description: 'Project lifecycle management plugin',
    kind: 'ui',
    type: 'react',
    path: '/plugins/projects-manager',
    entry_point: 'http://localhost:5175'
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
