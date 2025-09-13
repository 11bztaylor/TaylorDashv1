import React from 'react'
import { CheckCircle, XCircle, AlertCircle, Activity } from 'lucide-react'
import { MCPServer } from '../App'
import { clsx } from 'clsx'

interface MCPConnectionStatusProps {
  servers: MCPServer[]
}

export const MCPConnectionStatus: React.FC<MCPConnectionStatusProps> = ({ servers }) => {
  const onlineServers = servers.filter(s => s.status === 'online').length
  const offlineServers = servers.filter(s => s.status === 'offline').length
  const errorServers = servers.filter(s => s.status === 'error').length
  const connectingServers = servers.filter(s => s.status === 'connecting').length

  const totalServers = servers.length
  const healthPercentage = totalServers > 0 ? (onlineServers / totalServers) * 100 : 0

  const getHealthColor = () => {
    if (healthPercentage >= 80) return 'text-green-400 border-green-500/30'
    if (healthPercentage >= 50) return 'text-yellow-400 border-yellow-500/30'
    return 'text-red-400 border-red-500/30'
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <Activity className="w-5 h-5 text-cyan-400" />
        Network Status
      </h2>
      
      <div className="grid md:grid-cols-4 gap-6">
        {/* Overall Health */}
        <div className={clsx(
          'text-center p-4 rounded-lg border-2',
          getHealthColor(),
          healthPercentage >= 80 && 'bg-green-500/10',
          healthPercentage >= 50 && healthPercentage < 80 && 'bg-yellow-500/10',
          healthPercentage < 50 && 'bg-red-500/10'
        )}>
          <div className="text-2xl font-bold mb-1">
            {Math.round(healthPercentage)}%
          </div>
          <div className="text-sm text-gray-400">Network Health</div>
        </div>

        {/* Online Servers */}
        <div className="text-center p-4 rounded-lg border-2 border-green-500/30 bg-green-500/10">
          <div className="flex items-center justify-center mb-2">
            <CheckCircle className="w-5 h-5 text-green-400 mr-2" />
            <span className="text-2xl font-bold text-green-400">{onlineServers}</span>
          </div>
          <div className="text-sm text-gray-400">Online</div>
        </div>

        {/* Offline Servers */}
        <div className="text-center p-4 rounded-lg border-2 border-red-500/30 bg-red-500/10">
          <div className="flex items-center justify-center mb-2">
            <XCircle className="w-5 h-5 text-red-400 mr-2" />
            <span className="text-2xl font-bold text-red-400">{offlineServers}</span>
          </div>
          <div className="text-sm text-gray-400">Offline</div>
        </div>

        {/* Issues */}
        <div className="text-center p-4 rounded-lg border-2 border-yellow-500/30 bg-yellow-500/10">
          <div className="flex items-center justify-center mb-2">
            <AlertCircle className="w-5 h-5 text-yellow-400 mr-2" />
            <span className="text-2xl font-bold text-yellow-400">{errorServers + connectingServers}</span>
          </div>
          <div className="text-sm text-gray-400">Issues</div>
        </div>
      </div>

      {/* Health Bar */}
      <div className="mt-4">
        <div className="flex justify-between text-sm text-gray-400 mb-2">
          <span>System Health</span>
          <span>{onlineServers}/{totalServers} servers online</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div 
            className={clsx(
              'h-2 rounded-full transition-all duration-500',
              healthPercentage >= 80 && 'bg-green-500',
              healthPercentage >= 50 && healthPercentage < 80 && 'bg-yellow-500',
              healthPercentage < 50 && 'bg-red-500'
            )}
            style={{ width: `${healthPercentage}%` }}
          />
        </div>
      </div>
    </div>
  )
}