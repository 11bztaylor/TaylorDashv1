import { mqttService, TaylorDashEvent, ProjectEvent, SystemEvent } from './mqttService';

export interface PluginEventMessage {
  type: 'event';
  eventType: string;
  data: TaylorDashEvent;
  pluginId?: string;
}

export interface PluginSubscriptionMessage {
  type: 'subscribe' | 'unsubscribe';
  topics: string[];
  pluginId: string;
}

export interface PluginStatusMessage {
  type: 'status';
  status: 'ready' | 'error' | 'disconnected';
  pluginId: string;
}

type PluginMessage = PluginEventMessage | PluginSubscriptionMessage | PluginStatusMessage;

class EventBusService {
  private pluginSubscriptions = new Map<string, Set<string>>(); // pluginId -> Set of topics
  private pluginWindows = new Map<string, Window>(); // pluginId -> iframe window
  private mqttUnsubscribers = new Map<string, () => void>(); // topic -> unsubscriber function

  constructor() {
    this.initializeMQTTSubscriptions();
    this.setupPluginMessageListener();
  }

  private initializeMQTTSubscriptions() {
    // Subscribe to all relevant MQTT topics and forward to plugins
    const allTopics = [
      'tracker/events/projects/created',
      'tracker/events/projects/updated', 
      'tracker/events/projects/deleted',
      'tracker/events/system/health',
      'tracker/events/system/status',
      'system/connection_status'
    ];

    allTopics.forEach(topic => {
      const unsubscriber = mqttService.subscribe(topic, (event: TaylorDashEvent) => {
        this.broadcastEventToPlugins(topic, event);
      });
      this.mqttUnsubscribers.set(topic, unsubscriber);
    });

    console.log('[EventBus] Initialized MQTT subscriptions for topics:', allTopics);
  }

  private setupPluginMessageListener() {
    window.addEventListener('message', (event) => {
      // Security check - only accept messages from plugin iframes
      if (!this.isPluginOrigin(event.origin)) {
        return;
      }

      try {
        const message: PluginMessage = event.data;
        this.handlePluginMessage(message, event.source as Window);
      } catch (error) {
        console.error('[EventBus] Error handling plugin message:', error);
      }
    });
  }

  private isPluginOrigin(origin: string): boolean {
    // Accept messages from plugin development servers and production URLs
    const allowedOrigins = [
      'http://localhost:5173', // midnight-hud
      'http://localhost:5175', // projects-manager
      'https://taylordash.local', // production
      window.location.origin // same origin for production builds
    ];
    
    return allowedOrigins.includes(origin);
  }

  private handlePluginMessage(message: PluginMessage, source: Window) {
    switch (message.type) {
      case 'subscribe':
        this.handlePluginSubscribe(message as PluginSubscriptionMessage, source);
        break;
      case 'unsubscribe':
        this.handlePluginUnsubscribe(message as PluginSubscriptionMessage);
        break;
      case 'status':
        this.handlePluginStatus(message as PluginStatusMessage);
        break;
      default:
        console.warn('[EventBus] Unknown plugin message type:', message);
    }
  }

  private handlePluginSubscribe(message: PluginSubscriptionMessage, source: Window) {
    const { pluginId, topics } = message;
    
    if (!this.pluginSubscriptions.has(pluginId)) {
      this.pluginSubscriptions.set(pluginId, new Set());
    }
    
    if (!this.pluginWindows.has(pluginId)) {
      this.pluginWindows.set(pluginId, source);
    }

    const pluginTopics = this.pluginSubscriptions.get(pluginId)!;
    topics.forEach(topic => pluginTopics.add(topic));

    console.log(`[EventBus] Plugin ${pluginId} subscribed to topics:`, topics);
    
    // Send confirmation back to plugin
    this.sendMessageToPlugin(pluginId, {
      type: 'subscription_confirmed',
      topics: topics,
      status: 'success'
    });
  }

  private handlePluginUnsubscribe(message: PluginSubscriptionMessage) {
    const { pluginId, topics } = message;
    
    if (this.pluginSubscriptions.has(pluginId)) {
      const pluginTopics = this.pluginSubscriptions.get(pluginId)!;
      topics.forEach(topic => pluginTopics.delete(topic));
      
      if (pluginTopics.size === 0) {
        this.pluginSubscriptions.delete(pluginId);
        this.pluginWindows.delete(pluginId);
      }
    }

    console.log(`[EventBus] Plugin ${pluginId} unsubscribed from topics:`, topics);
  }

  private handlePluginStatus(message: PluginStatusMessage) {
    const { pluginId, status } = message;
    console.log(`[EventBus] Plugin ${pluginId} status: ${status}`);
    
    if (status === 'ready') {
      // Send initial connection status to newly ready plugin
      this.sendConnectionStatusToPlugin(pluginId);
    }
  }

  private broadcastEventToPlugins(topic: string, event: TaylorDashEvent) {
    this.pluginSubscriptions.forEach((topics, pluginId) => {
      if (topics.has(topic)) {
        this.sendEventToPlugin(pluginId, topic, event);
      }
    });
  }

  private sendEventToPlugin(pluginId: string, topic: string, event: TaylorDashEvent) {
    const message: PluginEventMessage = {
      type: 'event',
      eventType: event.type,
      data: event,
      pluginId: pluginId
    };

    this.sendMessageToPlugin(pluginId, {
      ...message,
      topic: topic
    });
  }

  private sendMessageToPlugin(pluginId: string, message: any) {
    const pluginWindow = this.pluginWindows.get(pluginId);
    if (pluginWindow) {
      try {
        pluginWindow.postMessage(message, '*');
      } catch (error) {
        console.error(`[EventBus] Failed to send message to plugin ${pluginId}:`, error);
        // Clean up dead plugin reference
        this.pluginSubscriptions.delete(pluginId);
        this.pluginWindows.delete(pluginId);
      }
    }
  }

  private sendConnectionStatusToPlugin(pluginId: string) {
    const statusEvent: SystemEvent = {
      id: `status_${Date.now()}`,
      type: 'connection_status',
      timestamp: new Date().toISOString(),
      data: {
        service: 'eventbus',
        status: mqttService.getConnectionStatus()
      }
    };

    this.sendEventToPlugin(pluginId, 'system/connection_status', statusEvent);
  }

  // Public API
  registerPlugin(pluginId: string, iframe: HTMLIFrameElement) {
    if (iframe.contentWindow) {
      this.pluginWindows.set(pluginId, iframe.contentWindow);
      console.log(`[EventBus] Registered plugin window: ${pluginId}`);
    }
  }

  unregisterPlugin(pluginId: string) {
    this.pluginSubscriptions.delete(pluginId);
    this.pluginWindows.delete(pluginId);
    console.log(`[EventBus] Unregistered plugin: ${pluginId}`);
  }

  // Test methods for development
  publishTestProjectEvent(eventType: 'created' | 'updated' | 'deleted', projectData: any) {
    const event: ProjectEvent = {
      id: `test_${Date.now()}`,
      type: `project_${eventType}`,
      timestamp: new Date().toISOString(),
      data: {
        project_id: projectData.id || 'test-project-123',
        project_name: projectData.name || 'Test Project',
        status: projectData.status || 'active',
        ...projectData
      },
      trace_id: `eventbus_test_${Date.now()}`
    };

    // Broadcast to plugins immediately (simulate MQTT event)
    this.broadcastEventToPlugins(`tracker/events/projects/${eventType}`, event);
    
    // Also publish to MQTT for backend processing
    mqttService.publishTestEvent(`projects/${eventType}`, event.data);
  }

  getStats() {
    return {
      connectedPlugins: this.pluginSubscriptions.size,
      totalSubscriptions: Array.from(this.pluginSubscriptions.values())
        .reduce((total, topics) => total + topics.size, 0),
      mqttStatus: mqttService.getConnectionStatus(),
      topics: Array.from(this.mqttUnsubscribers.keys())
    };
  }

  disconnect() {
    // Unsubscribe from all MQTT topics
    this.mqttUnsubscribers.forEach(unsubscriber => unsubscriber());
    this.mqttUnsubscribers.clear();
    
    // Clear plugin subscriptions
    this.pluginSubscriptions.clear();
    this.pluginWindows.clear();
    
    console.log('[EventBus] Disconnected and cleaned up');
  }
}

// Export singleton instance
export const eventBusService = new EventBusService();
export default eventBusService;