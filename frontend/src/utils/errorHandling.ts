/**
 * Frontend error handling utilities for TaylorDash
 * Provides error boundaries, API error handling, and user notifications
 */

// Error types and interfaces
export interface ErrorContext {
  component?: string;
  action?: string;
  endpoint?: string;
  method?: string;
  userAgent?: string;
  timestamp: string;
  userId?: string;
  sessionId?: string;
}

export interface AppError {
  code: string;
  message: string;
  details?: string;
  category: 'API' | 'VALIDATION' | 'NETWORK' | 'COMPONENT' | 'SYSTEM';
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  context: ErrorContext;
  originalError?: Error;
}

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: string;
    timestamp: string;
    trace_id: string;
    category: string;
    severity: string;
    context?: any;
    suggestions?: string[];
  };
}

// Error factory functions
export const createError = (
  code: string,
  message: string,
  category: AppError['category'],
  severity: AppError['severity'],
  context: Partial<ErrorContext> = {},
  originalError?: Error
): AppError => ({
  code,
  message,
  category,
  severity,
  context: {
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    ...context
  },
  originalError
});

export const createApiError = (
  response: Response,
  endpoint: string,
  method: string,
  responseData?: ApiErrorResponse
): AppError => {
  const baseMessage = `${method} ${endpoint} failed with status ${response.status}`;
  
  if (responseData?.error) {
    return createError(
      responseData.error.code,
      responseData.error.message,
      'API',
      responseData.error.severity as AppError['severity'],
      {
        endpoint,
        method,
        statusCode: response.status,
        traceId: responseData.error.trace_id,
        ...responseData.error.context
      }
    );
  }
  
  // Default error for non-standard responses
  return createError(
    'API_ERROR',
    baseMessage,
    'API',
    response.status >= 500 ? 'HIGH' : 'MEDIUM',
    { endpoint, method, statusCode: response.status }
  );
};

export const createNetworkError = (
  endpoint: string,
  method: string,
  originalError: Error
): AppError => createError(
  'NETWORK_ERROR',
  'Network request failed - please check your connection',
  'NETWORK',
  'HIGH',
  { endpoint, method },
  originalError
);

export const createValidationError = (
  field: string,
  message: string,
  component?: string
): AppError => createError(
  'VALIDATION_ERROR',
  message,
  'VALIDATION',
  'MEDIUM',
  { field, component }
);

// Error logging utilities
class ErrorLogger {
  private static instance: ErrorLogger;
  private logBuffer: AppError[] = [];
  private maxBufferSize = 50;
  private flushInterval = 30000; // 30 seconds

  static getInstance(): ErrorLogger {
    if (!ErrorLogger.instance) {
      ErrorLogger.instance = new ErrorLogger();
    }
    return ErrorLogger.instance;
  }

  private constructor() {
    // Start periodic flush
    setInterval(() => {
      this.flush();
    }, this.flushInterval);

    // Flush on page unload
    window.addEventListener('beforeunload', () => {
      this.flush(true);
    });
  }

  log(error: AppError): void {
    // Add to buffer
    this.logBuffer.push(error);

    // Immediate flush for critical errors
    if (error.severity === 'CRITICAL') {
      this.flush();
    }

    // Prevent buffer overflow
    if (this.logBuffer.length > this.maxBufferSize) {
      this.logBuffer = this.logBuffer.slice(-this.maxBufferSize);
    }

    // Console logging for development
    if (process.env.NODE_ENV === 'development') {
      const logMethod = error.severity === 'CRITICAL' || error.severity === 'HIGH' 
        ? console.error 
        : error.severity === 'MEDIUM' 
        ? console.warn 
        : console.info;

      logMethod('Frontend Error:', {
        code: error.code,
        message: error.message,
        category: error.category,
        severity: error.severity,
        context: error.context,
        stack: error.originalError?.stack
      });
    }
  }

  private async flush(sync: boolean = false): Promise<void> {
    if (this.logBuffer.length === 0) return;

    const errors = [...this.logBuffer];
    this.logBuffer = [];

    const logData = {
      errors: errors.map(error => ({
        timestamp: error.context.timestamp,
        level: 'ERROR',
        service: 'taylordash-frontend',
        category: error.category,
        severity: error.severity,
        message: error.message,
        details: error.details,
        error_code: error.code,
        context: {
          ...error.context,
          stack_trace: error.originalError?.stack,
          url: window.location.href,
          user_agent: navigator.userAgent
        }
      }))
    };

    try {
      const method = sync ? 'sendBeacon' : 'fetch';
      
      if (sync && navigator.sendBeacon) {
        navigator.sendBeacon(
          '/api/v1/logs/frontend',
          JSON.stringify(logData)
        );
      } else {
        await fetch('/api/v1/logs/frontend', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': 'taylordash-dev-key' // TODO: Get from config
          },
          body: JSON.stringify(logData)
        });
      }
    } catch (e) {
      // Store in localStorage as fallback
      try {
        const stored = localStorage.getItem('taylordash_error_logs') || '[]';
        const existingLogs = JSON.parse(stored);
        const updatedLogs = [...existingLogs, ...logData.errors].slice(-100); // Keep last 100
        localStorage.setItem('taylordash_error_logs', JSON.stringify(updatedLogs));
      } catch (storageError) {
        console.error('Failed to store error logs:', storageError);
      }
    }
  }
}

// Global error logger instance
export const errorLogger = ErrorLogger.getInstance();

// API helper with error handling
export const apiCall = async <T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const method = options.method || 'GET';
  const url = endpoint.startsWith('http') ? endpoint : `/api/v1${endpoint}`;

  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': 'taylordash-dev-key', // TODO: Get from config
        ...options.headers
      },
      ...options
    });

    if (!response.ok) {
      let errorData: ApiErrorResponse | undefined;
      try {
        errorData = await response.json();
      } catch (e) {
        // Response body isn't JSON
      }

      const error = createApiError(response, endpoint, method, errorData);
      errorLogger.log(error);
      throw error;
    }

    return await response.json();
  } catch (error) {
    if (error instanceof AppError) {
      throw error; // Re-throw our structured errors
    }

    // Handle network errors
    const networkError = createNetworkError(endpoint, method, error as Error);
    errorLogger.log(networkError);
    throw networkError;
  }
};

// User notification utilities
export interface Notification {
  id: string;
  type: 'error' | 'warning' | 'info' | 'success';
  title: string;
  message: string;
  duration?: number;
  actions?: Array<{
    label: string;
    action: () => void;
  }>;
}

class NotificationManager {
  private static instance: NotificationManager;
  private notifications: Map<string, Notification> = new Map();
  private listeners: Set<(notifications: Notification[]) => void> = new Set();

  static getInstance(): NotificationManager {
    if (!NotificationManager.instance) {
      NotificationManager.instance = new NotificationManager();
    }
    return NotificationManager.instance;
  }

  show(notification: Omit<Notification, 'id'>): string {
    const id = Date.now().toString();
    const fullNotification: Notification = {
      id,
      duration: 5000, // Default 5 seconds
      ...notification
    };

    this.notifications.set(id, fullNotification);
    this.notifyListeners();

    // Auto-remove after duration
    if (fullNotification.duration && fullNotification.duration > 0) {
      setTimeout(() => {
        this.remove(id);
      }, fullNotification.duration);
    }

    return id;
  }

  remove(id: string): void {
    this.notifications.delete(id);
    this.notifyListeners();
  }

  clear(): void {
    this.notifications.clear();
    this.notifyListeners();
  }

  subscribe(listener: (notifications: Notification[]) => void): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notifyListeners(): void {
    const notifications = Array.from(this.notifications.values());
    this.listeners.forEach(listener => listener(notifications));
  }

  // Helper methods for common notification types
  showError(error: AppError): string {
    return this.show({
      type: 'error',
      title: 'Error',
      message: error.message,
      duration: error.severity === 'CRITICAL' ? 0 : 8000 // Persistent for critical
    });
  }

  showSuccess(message: string, title = 'Success'): string {
    return this.show({
      type: 'success',
      title,
      message,
      duration: 3000
    });
  }

  showWarning(message: string, title = 'Warning'): string {
    return this.show({
      type: 'warning',
      title,
      message,
      duration: 5000
    });
  }

  showInfo(message: string, title = 'Info'): string {
    return this.show({
      type: 'info',
      title,
      message,
      duration: 4000
    });
  }
}

export const notificationManager = NotificationManager.getInstance();

// Recovery strategies
export const withRetry = async <T>(
  operation: () => Promise<T>,
  maxAttempts: number = 3,
  delay: number = 1000
): Promise<T> => {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await operation();
    } catch (error) {
      if (attempt === maxAttempts) {
        throw error;
      }
      
      // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, attempt - 1)));
    }
  }
  
  throw new Error('Max retry attempts exceeded');
};

export const withFallback = async <T>(
  primary: () => Promise<T>,
  fallback: () => Promise<T> | T
): Promise<T> => {
  try {
    return await primary();
  } catch (error) {
    console.warn('Primary operation failed, using fallback:', error);
    return await fallback();
  }
};

// Performance monitoring
export const measurePerformance = <T>(
  operation: () => T,
  label: string,
  threshold: number = 1000
): T => {
  const start = performance.now();
  const result = operation();
  const duration = performance.now() - start;
  
  if (duration > threshold) {
    const error = createError(
      'PERFORMANCE_WARNING',
      `Slow operation detected: ${label} took ${duration.toFixed(2)}ms`,
      'SYSTEM',
      'MEDIUM',
      { operation: label, duration, threshold }
    );
    errorLogger.log(error);
  }
  
  return result;
};

export const measureAsyncPerformance = async <T>(
  operation: () => Promise<T>,
  label: string,
  threshold: number = 1000
): Promise<T> => {
  const start = performance.now();
  const result = await operation();
  const duration = performance.now() - start;
  
  if (duration > threshold) {
    const error = createError(
      'PERFORMANCE_WARNING',
      `Slow async operation detected: ${label} took ${duration.toFixed(2)}ms`,
      'SYSTEM',
      'MEDIUM',
      { operation: label, duration, threshold }
    );
    errorLogger.log(error);
  }
  
  return result;
};