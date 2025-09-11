// Plugin Event Service - Handles communication with TaylorDash Event Bus

export interface TaylorDashEvent {
  id: string;
  type: string;
  timestamp: string;
  data: any;
  trace_id?: string;
}

export interface ProjectEvent extends TaylorDashEvent {
  type: 'project_created' | 'project_updated' | 'project_deleted';
  data: {
    project_id: string;
    project_name: string;
    status?: string;
    [key: string]: any;
  };
}

export interface EventMessage {
  type: 'event';
  eventType: string;
  data: TaylorDashEvent;
  topic?: string;
  pluginId?: string;
}

export interface SubscriptionConfirmation {
  type: 'subscription_confirmed';
  topics: string[];
  status: 'success' | 'error';
}

type EventCallback = (event: TaylorDashEvent) => void;
type PluginMessage = EventMessage | SubscriptionConfirmation;

class PluginEventService {
  private subscriptions = new Map<string, Set<EventCallback>>();
  private isReady = false;
  private pluginId = 'projects-manager';
  private pendingSubscriptions: string[] = [];

  constructor() {
    this.initializeEventListener();
    this.notifyReady();
  }

  private initializeEventListener() {
    window.addEventListener('message', (event) => {
      // Accept messages from the main TaylorDash application
      if (!this.isValidOrigin(event.origin)) {
        return;
      }

      try {
        const message: PluginMessage = event.data;
        this.handleMessage(message);
      } catch (error) {
        console.error('[PluginEventService] Error handling message:', error);
      }
    });
  }

  private isValidOrigin(origin: string): boolean {
    // Accept messages from the main TaylorDash application
    const allowedOrigins = [
      'http://localhost:5174', // main frontend dev
      'http://localhost:5173', // alternate dev port
      'https://taylordash.local', // production
      window.location.origin // same origin
    ];
    
    return allowedOrigins.includes(origin);
  }

  private handleMessage(message: PluginMessage) {
    switch (message.type) {
      case 'event':
        this.handleEventMessage(message as EventMessage);
        break;
      case 'subscription_confirmed':
        this.handleSubscriptionConfirmation(message as SubscriptionConfirmation);
        break;
      default:
        console.warn('[PluginEventService] Unknown message type:', message);
    }
  }

  private handleEventMessage(message: EventMessage) {
    const { topic = '', data } = message;
    
    console.log(`[PluginEventService] Received event on topic ${topic}:`, data);
    
    // Notify all subscribers for this topic
    const callbacks = this.subscriptions.get(topic);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`[PluginEventService] Error in event callback for topic ${topic}:`, error);
        }
      });
    }
  }

  private handleSubscriptionConfirmation(message: SubscriptionConfirmation) {
    console.log(`[PluginEventService] Subscription confirmed:`, message);
  }

  private notifyReady() {
    // Let the main application know this plugin is ready
    this.sendMessage({
      type: 'status',
      status: 'ready',
      pluginId: this.pluginId
    });

    this.isReady = true;
    
    // Subscribe to any pending topics
    if (this.pendingSubscriptions.length > 0) {
      this.subscribe(this.pendingSubscriptions);
      this.pendingSubscriptions = [];
    }
  }

  private sendMessage(message: any) {
    // Send message to parent window (main TaylorDash application)
    if (window.parent && window.parent !== window) {
      window.parent.postMessage(message, '*');
    }
  }

  // Public API
  subscribe(topics: string | string[], callback?: EventCallback): () => void {
    const topicArray = Array.isArray(topics) ? topics : [topics];
    
    if (!this.isReady) {
      this.pendingSubscriptions.push(...topicArray);
      return () => {}; // Return empty unsubscriber
    }

    // Add callback to subscriptions
    if (callback) {
      topicArray.forEach(topic => {
        if (!this.subscriptions.has(topic)) {
          this.subscriptions.set(topic, new Set());
        }
        this.subscriptions.get(topic)!.add(callback);
      });
    }

    // Send subscription message to main application
    this.sendMessage({
      type: 'subscribe',
      topics: topicArray,
      pluginId: this.pluginId
    });

    console.log(`[PluginEventService] Subscribed to topics:`, topicArray);

    // Return unsubscriber function
    return () => {
      if (callback) {
        topicArray.forEach(topic => {
          const callbacks = this.subscriptions.get(topic);
          if (callbacks) {
            callbacks.delete(callback);
            if (callbacks.size === 0) {
              this.subscriptions.delete(topic);
            }
          }
        });
      }

      this.sendMessage({
        type: 'unsubscribe',
        topics: topicArray,
        pluginId: this.pluginId
      });

      console.log(`[PluginEventService] Unsubscribed from topics:`, topicArray);
    };
  }

  // Convenience methods
  subscribeToProjectEvents(callback: (event: ProjectEvent) => void): () => void {
    const topics = [
      'tracker/events/projects/created',
      'tracker/events/projects/updated',
      'tracker/events/projects/deleted'
    ];

    return this.subscribe(topics, callback as EventCallback);
  }

  subscribeToSystemEvents(callback: (event: TaylorDashEvent) => void): () => void {
    const topics = [
      'tracker/events/system/health',
      'tracker/events/system/status',
      'system/connection_status'
    ];

    return this.subscribe(topics, callback);
  }

  getConnectionStatus(): 'ready' | 'connecting' | 'disconnected' {
    return this.isReady ? 'ready' : 'connecting';
  }
}

// Export singleton instance
export const pluginEventService = new PluginEventService();
export default pluginEventService;