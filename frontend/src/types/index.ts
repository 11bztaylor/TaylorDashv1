// Core application types for TaylorDash

export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  preferences: UserPreferences;
}

export interface UserPreferences {
  theme: 'midnight' | 'cyber';
  language: string;
  notifications: boolean;
  autoSave: boolean;
  gridSize: number;
}

export interface Widget {
  id: string;
  type: string;
  title: string;
  position: Position;
  size: Size;
  config: Record<string, any>;
  isVisible: boolean;
  isLocked: boolean;
}

export interface Position {
  x: number;
  y: number;
  z?: number;
}

export interface Size {
  width: number;
  height: number;
}

export interface Canvas {
  id: string;
  name: string;
  description?: string;
  widgets: Widget[];
  settings: CanvasSettings;
  createdAt: string;
  updatedAt: string;
}

export interface CanvasSettings {
  background: string;
  gridVisible: boolean;
  snapToGrid: boolean;
  gridSize: number;
  zoom: number;
  viewPosition: Position;
}

export interface Plugin {
  id: string;
  name: string;
  version: string;
  description: string;
  author: string;
  category: PluginCategory;
  isEnabled: boolean;
  config: Record<string, any>;
  permissions: PluginPermission[];
}

export enum PluginCategory {
  WIDGET = 'widget',
  TOOL = 'tool',
  INTEGRATION = 'integration',
  THEME = 'theme',
  UTILITY = 'utility'
}

export enum PluginPermission {
  FILE_SYSTEM = 'file_system',
  NETWORK = 'network',
  NOTIFICATIONS = 'notifications',
  CLIPBOARD = 'clipboard',
  SYSTEM_INFO = 'system_info'
}

export interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  isActive: boolean;
  badge?: number;
}

export interface Theme {
  name: string;
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    surface: string;
    text: string;
    border: string;
  };
  fonts: {
    sans: string;
    mono: string;
  };
}

export interface AppState {
  user: User | null;
  currentCanvas: Canvas | null;
  canvases: Canvas[];
  plugins: Plugin[];
  isLoading: boolean;
  error: string | null;
}

// React Flow types
export interface FlowNode {
  id: string;
  type: string;
  position: Position;
  data: any;
  selected?: boolean;
  dragging?: boolean;
}

export interface FlowEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
  animated?: boolean;
  style?: Record<string, any>;
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Event types
export interface AppEvent {
  type: string;
  payload: any;
  timestamp: number;
}

export interface WidgetEvent extends AppEvent {
  widgetId: string;
}

export interface CanvasEvent extends AppEvent {
  canvasId: string;
}