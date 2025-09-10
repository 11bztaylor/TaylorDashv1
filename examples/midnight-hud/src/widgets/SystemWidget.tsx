import React from 'react';
import { Cpu, HardDrive, Wifi, Clock } from 'lucide-react';
import type { SystemData } from '../types/dashboard';

interface SystemWidgetProps {
  data: SystemData;
  isMinimized: boolean;
}

export const SystemWidget: React.FC<SystemWidgetProps> = ({ data, isMinimized }) => {
  if (isMinimized) {
    return (
      <div className="flex items-center space-x-2 p-2">
        <Cpu className="w-4 h-4 text-cyan-400" />
        <span className="text-sm text-white">{data.cpu}%</span>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-3">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <span className="text-sm text-gray-300">CPU</span>
          </div>
          <div className="text-lg font-mono text-white">{data.cpu}%</div>
        </div>
        
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <HardDrive className="w-4 h-4 text-green-400" />
            <span className="text-sm text-gray-300">Memory</span>
          </div>
          <div className="text-lg font-mono text-white">{data.memory}%</div>
        </div>
        
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Wifi className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-gray-300">Network</span>
          </div>
          <div className="text-xs font-mono text-white">
            ↑{data.network.up} ↓{data.network.down}
          </div>
        </div>
        
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-orange-400" />
            <span className="text-sm text-gray-300">Uptime</span>
          </div>
          <div className="text-xs font-mono text-white">{data.uptime}</div>
        </div>
      </div>
    </div>
  );
};