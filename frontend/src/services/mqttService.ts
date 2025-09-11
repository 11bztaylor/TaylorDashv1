import mqtt from 'mqtt';

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

export interface SystemEvent extends TaylorDashEvent {
  type: 'system_health' | 'connection_status' | 'service_status';
  data: {
    service?: string;
    status: string;
    [key: string]: any;
  };
}

type EventCallback = (event: TaylorDashEvent) => void;
type EventSubscription = {
  topic: string;
  callback: EventCallback;
};

class MQTTService {
  private client: mqtt.MqttClient | null = null;
  private subscriptions: EventSubscription[] = [];
  private connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error' = 'disconnected';
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor() {
    this.connect();
  }

  private connect() {
    try {
      this.connectionStatus = 'connecting';
      console.log('[MQTT] Connecting to WebSocket broker...');

      this.client = mqtt.connect('ws://localhost:9001', {
        username: 'taylordash',
        password: 'taylordash',
        clientId: `taylordash_frontend_${Math.random().toString(16).substr(2, 8)}`,
        clean: true,
        connectTimeout: 10000,
        keepalive: 60,
        reconnectPeriod: 0, // We'll handle reconnection manually
      });

      this.client.on('connect', () => {
        console.log('[MQTT] Connected to broker');
        this.connectionStatus = 'connected';
        this.reconnectAttempts = 0;
        this.resubscribe();
        this.notifyConnectionStatus('connected');
      });

      this.client.on('message', (topic, message) => {
        try {
          const eventData = JSON.parse(message.toString());
          const event: TaylorDashEvent = {
            id: eventData.id || `${Date.now()}_${Math.random()}`,
            type: this.extractEventType(topic),
            timestamp: eventData.timestamp || new Date().toISOString(),
            data: eventData,
            trace_id: eventData.trace_id
          };

          console.log(`[MQTT] Received event on ${topic}:`, event);
          this.handleEvent(topic, event);
        } catch (error) {
          console.error('[MQTT] Failed to parse message:', error);
        }
      });

      this.client.on('error', (error) => {
        console.error('[MQTT] Connection error:', error);
        this.connectionStatus = 'error';
        this.notifyConnectionStatus('error');
        this.attemptReconnect();
      });

      this.client.on('close', () => {
        console.log('[MQTT] Connection closed');
        this.connectionStatus = 'disconnected';
        this.notifyConnectionStatus('disconnected');
        this.attemptReconnect();
      });

    } catch (error) {
      console.error('[MQTT] Failed to create connection:', error);
      this.connectionStatus = 'error';
      this.attemptReconnect();
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      
      console.log(`[MQTT] Attempting reconnect ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`);
      
      setTimeout(() => {
        this.connect();
      }, delay);
    } else {
      console.error('[MQTT] Max reconnection attempts reached');
      this.connectionStatus = 'error';
      this.notifyConnectionStatus('error');
    }
  }

  private resubscribe() {
    if (this.client && this.connectionStatus === 'connected') {
      const topics = [...new Set(this.subscriptions.map(sub => sub.topic))];
      topics.forEach(topic => {
        this.client!.subscribe(topic, (error) => {
          if (error) {
            console.error(`[MQTT] Failed to subscribe to ${topic}:`, error);
          } else {
            console.log(`[MQTT] Subscribed to ${topic}`);
          }
        });
      });
    }
  }

  private extractEventType(topic: string): string {
    const parts = topic.split('/');
    return parts[parts.length - 1] || 'unknown';
  }

  private handleEvent(topic: string, event: TaylorDashEvent) {
    this.subscriptions
      .filter(sub => sub.topic === topic)
      .forEach(sub => {
        try {
          sub.callback(event);
        } catch (error) {
          console.error('[MQTT] Error in event callback:', error);
        }
      });
  }

  private notifyConnectionStatus(status: string) {
    const statusEvent: SystemEvent = {
      id: `mqtt_status_${Date.now()}`,
      type: 'connection_status',
      timestamp: new Date().toISOString(),
      data: {
        service: 'mqtt',
        status: status
      }
    };

    this.handleEvent('system/connection_status', statusEvent);
  }

  // Public API
  subscribe(topic: string, callback: EventCallback): () => void {
    const subscription: EventSubscription = { topic, callback };
    this.subscriptions.push(subscription);

    if (this.client && this.connectionStatus === 'connected') {
      this.client.subscribe(topic, (error) => {
        if (error) {
          console.error(`[MQTT] Failed to subscribe to ${topic}:`, error);
        } else {
          console.log(`[MQTT] Subscribed to ${topic}`);
        }
      });
    }

    // Return unsubscribe function
    return () => {
      const index = this.subscriptions.indexOf(subscription);
      if (index > -1) {
        this.subscriptions.splice(index, 1);
        
        // Unsubscribe from MQTT if no other subscriptions for this topic
        const hasOtherSubs = this.subscriptions.some(sub => sub.topic === topic);
        if (!hasOtherSubs && this.client && this.connectionStatus === 'connected') {
          this.client.unsubscribe(topic);
          console.log(`[MQTT] Unsubscribed from ${topic}`);
        }
      }
    };
  }

  // Convenience methods for common subscriptions
  subscribeToProjectEvents(callback: (event: ProjectEvent) => void): () => void {
    const unsubscribers = [
      this.subscribe('tracker/events/projects/created', callback as EventCallback),
      this.subscribe('tracker/events/projects/updated', callback as EventCallback),
      this.subscribe('tracker/events/projects/deleted', callback as EventCallback)
    ];

    return () => unsubscribers.forEach(unsub => unsub());
  }

  subscribeToSystemEvents(callback: (event: SystemEvent) => void): () => void {
    const unsubscribers = [
      this.subscribe('tracker/events/system/health', callback as EventCallback),
      this.subscribe('tracker/events/system/status', callback as EventCallback),
      this.subscribe('system/connection_status', callback as EventCallback)
    ];

    return () => unsubscribers.forEach(unsub => unsub());
  }

  // Publish a test event (for development/testing)
  publishTestEvent(eventType: string, data: any): void {
    if (this.client && this.connectionStatus === 'connected') {
      const event = {
        id: `test_${Date.now()}`,
        type: eventType,
        timestamp: new Date().toISOString(),
        data: data,
        trace_id: `frontend_${Date.now()}`
      };

      this.client.publish(`tracker/events/test/${eventType}`, JSON.stringify(event));
      console.log(`[MQTT] Published test event:`, event);
    } else {
      console.warn('[MQTT] Cannot publish - not connected');
    }
  }

  getConnectionStatus(): string {
    return this.connectionStatus;
  }

  disconnect(): void {
    if (this.client) {
      this.client.end();
      this.client = null;
    }
    this.connectionStatus = 'disconnected';
    this.subscriptions = [];
  }
}

// Export singleton instance
export const mqttService = new MQTTService();
export default mqttService;