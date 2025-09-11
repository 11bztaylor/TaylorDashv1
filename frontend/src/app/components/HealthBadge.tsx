interface HealthBadgeProps {
  status: 'healthy' | 'unhealthy';
}

export function HealthBadge({ status }: HealthBadgeProps) {
  const isHealthy = status === 'healthy';
  
  return (
    <span 
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
        isHealthy 
          ? 'bg-green-100 text-green-800' 
          : 'bg-red-100 text-red-800'
      }`}
    >
      {isHealthy ? 'Healthy' : 'Unhealthy'}
    </span>
  );
}