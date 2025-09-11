import { useState, useEffect } from 'react';
import { Card } from '../components/Card';
import { HealthBadge } from '../components/HealthBadge';
import { fetchHealthStatus } from '../../lib/api';

interface HealthService {
  name: string;
  status: 'healthy' | 'unhealthy';
  detail: string;
  notes?: string;
}

interface HealthData {
  services: HealthService[];
}

export function Status() {
  const [healthData, setHealthData] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadHealthData() {
      try {
        setLoading(true);
        const response = await fetchHealthStatus();
        
        if (response.error) {
          setError(response.error);
        } else {
          setHealthData(response.data);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch health data');
      } finally {
        setLoading(false);
      }
    }

    loadHealthData();
  }, []);

  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Status</h1>
        <div className="text-slate-300">Loading health status...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Status</h1>
        <Card>
          <div className="text-red-400">Error: {error}</div>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Status</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {healthData?.services?.map((service, index) => (
          <Card key={index}>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">{service.name}</h3>
                <HealthBadge status={service.status} />
              </div>
              
              <p className="text-slate-300 text-sm">{service.detail}</p>
              
              {service.notes && (
                <p className="text-slate-400 text-xs">{service.notes}</p>
              )}
            </div>
          </Card>
        ))}
      </div>
      
      {(!healthData?.services || healthData.services.length === 0) && (
        <Card>
          <div className="text-slate-300">No services found</div>
        </Card>
      )}
    </div>
  );
}