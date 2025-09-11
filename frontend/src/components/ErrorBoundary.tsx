/**
 * Error Boundary components for React error handling
 */
import React, { Component, ReactNode, ErrorInfo } from 'react';
import { createError, errorLogger, notificationManager } from '../utils/errorHandling';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string | null;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: Error, errorInfo: ErrorInfo, retry: () => void) => ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  showNotification?: boolean;
  component?: string;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const { onError, showNotification = true, component } = this.props;

    // Create structured error
    const appError = createError(
      'COMPONENT_ERROR',
      `Component crashed: ${error.message}`,
      'COMPONENT',
      'HIGH',
      {
        component: component || 'Unknown',
        componentStack: errorInfo.componentStack,
        errorBoundary: this.constructor.name
      },
      error
    );

    // Log the error
    errorLogger.log(appError);

    // Show user notification
    if (showNotification) {
      notificationManager.showError(appError);
    }

    // Call custom error handler
    if (onError) {
      onError(error, errorInfo);
    }

    this.setState({
      error,
      errorInfo,
      errorId: Date.now().toString()
    });
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null
    });
  };

  render() {
    const { hasError, error, errorInfo } = this.state;
    const { children, fallback } = this.props;

    if (hasError && error && errorInfo) {
      if (fallback) {
        return fallback(error, errorInfo, this.handleRetry);
      }

      return (
        <DefaultErrorFallback
          error={error}
          errorInfo={errorInfo}
          onRetry={this.handleRetry}
        />
      );
    }

    return children;
  }
}

// Default error fallback component
interface DefaultErrorFallbackProps {
  error: Error;
  errorInfo: ErrorInfo;
  onRetry: () => void;
}

const DefaultErrorFallback: React.FC<DefaultErrorFallbackProps> = ({
  error,
  errorInfo,
  onRetry
}) => (
  <div className="bg-red-50 border border-red-200 rounded-lg p-6 m-4">
    <div className="flex items-center mb-4">
      <div className="flex-shrink-0">
        <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
      </div>
      <div className="ml-3">
        <h3 className="text-sm font-medium text-red-800">
          Something went wrong
        </h3>
      </div>
    </div>
    
    <div className="mb-4">
      <p className="text-sm text-red-700">
        {error.message || 'An unexpected error occurred'}
      </p>
    </div>

    <div className="flex space-x-3">
      <button
        onClick={onRetry}
        className="bg-red-100 hover:bg-red-200 text-red-800 px-4 py-2 rounded text-sm font-medium transition-colors"
      >
        Try Again
      </button>
      
      <button
        onClick={() => window.location.reload()}
        className="bg-gray-100 hover:bg-gray-200 text-gray-800 px-4 py-2 rounded text-sm font-medium transition-colors"
      >
        Refresh Page
      </button>
    </div>

    {process.env.NODE_ENV === 'development' && (
      <details className="mt-4">
        <summary className="text-sm text-red-700 cursor-pointer">
          Developer Details
        </summary>
        <pre className="mt-2 text-xs text-red-600 bg-red-100 p-2 rounded overflow-auto max-h-40">
          {error.stack}
        </pre>
        {errorInfo.componentStack && (
          <pre className="mt-2 text-xs text-red-600 bg-red-100 p-2 rounded overflow-auto max-h-40">
            {errorInfo.componentStack}
          </pre>
        )}
      </details>
    )}
  </div>
);

// Hook for error handling in functional components
export const useErrorHandler = (component?: string) => {
  const handleError = React.useCallback((error: Error, context?: any) => {
    const appError = createError(
      'HOOK_ERROR',
      error.message,
      'COMPONENT',
      'MEDIUM',
      {
        component: component || 'Unknown',
        hook: 'useErrorHandler',
        ...context
      },
      error
    );

    errorLogger.log(appError);
    notificationManager.showError(appError);
  }, [component]);

  return handleError;
};

// Async error boundary for handling promise rejections
export const AsyncErrorBoundary: React.FC<{
  children: ReactNode;
  fallback?: ReactNode;
}> = ({ children, fallback }) => {
  const [error, setError] = React.useState<Error | null>(null);

  React.useEffect(() => {
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      const error = event.reason instanceof Error 
        ? event.reason 
        : new Error(String(event.reason));

      const appError = createError(
        'UNHANDLED_PROMISE',
        'Unhandled promise rejection',
        'SYSTEM',
        'HIGH',
        { reason: event.reason },
        error
      );

      errorLogger.log(appError);
      setError(error);
    };

    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, []);

  if (error) {
    return fallback || (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 m-4">
        <div className="text-sm text-yellow-800">
          An unexpected error occurred. Please refresh the page.
        </div>
        <button
          onClick={() => window.location.reload()}
          className="mt-2 bg-yellow-100 hover:bg-yellow-200 text-yellow-800 px-3 py-1 rounded text-sm"
        >
          Refresh
        </button>
      </div>
    );
  }

  return <>{children}</>;
};

// Higher-order component for wrapping components with error boundaries
export const withErrorBoundary = <P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<ErrorBoundaryProps, 'children'>
) => {
  const WrappedComponent: React.FC<P> = (props) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;

  return WrappedComponent;
};

// Notification display component
export const NotificationContainer: React.FC = () => {
  const [notifications, setNotifications] = React.useState<any[]>([]);

  React.useEffect(() => {
    const unsubscribe = notificationManager.subscribe(setNotifications);
    return unsubscribe;
  }, []);

  if (notifications.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-md">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`p-4 rounded-lg shadow-lg border ${
            notification.type === 'error'
              ? 'bg-red-100 border-red-200 text-red-800'
              : notification.type === 'warning'
              ? 'bg-yellow-100 border-yellow-200 text-yellow-800'
              : notification.type === 'success'
              ? 'bg-green-100 border-green-200 text-green-800'
              : 'bg-blue-100 border-blue-200 text-blue-800'
          }`}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className="font-medium text-sm">{notification.title}</h4>
              <p className="text-sm mt-1">{notification.message}</p>
              
              {notification.actions && (
                <div className="mt-3 space-x-2">
                  {notification.actions.map((action: any, index: number) => (
                    <button
                      key={index}
                      onClick={action.action}
                      className="text-sm font-medium underline hover:no-underline"
                    >
                      {action.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
            
            <button
              onClick={() => notificationManager.remove(notification.id)}
              className="ml-4 text-gray-400 hover:text-gray-600"
            >
              <span className="sr-only">Close</span>
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};