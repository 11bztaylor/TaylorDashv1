export interface Plugin {
  id: string;
  name: string;
  kind: 'ui' | 'data' | 'integration';
  path: string;
  description?: string;
  version?: string;
  permissions?: string[];
}

export const PLUGINS: Plugin[] = [
  {
    id: "midnight-hud",
    name: "Midnight HUD",
    kind: "ui",
    path: "/plugins/midnight-hud",
    description: "Cyber-aesthetic dashboard with drag-and-drop widgets",
    version: "0.1.0",
    permissions: ["viewer"]
  }
];

export function getPluginById(id: string): Plugin | undefined {
  return PLUGINS.find(plugin => plugin.id === id);
}

export function getPluginsByKind(kind: Plugin['kind']): Plugin[] {
  return PLUGINS.filter(plugin => plugin.kind === kind);
}

export function hasPermission(plugin: Plugin, userRole: string): boolean {
  if (!plugin.permissions) return true;
  return plugin.permissions.includes(userRole) || plugin.permissions.includes('viewer');
}