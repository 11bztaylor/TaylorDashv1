import React from 'react'
import { RefreshCw, Wifi, WifiOff, AlertCircle, Clock, Server } from 'lucide-react'
import { MCPServer } from '../App'
import { clsx } from 'clsx'

interface MCPServerCardProps {
  server: MCPServer
  isSelected: boolean
  onSelect: () => void
  onRefresh: () => void
}

export const MCPServerCard: React.FC<MCPServerCardProps> = ({
  server,
  isSelected,
  onSelect,
  onRefresh
}) => {
  const getStatusIcon = () => {
    switch (server.status) {
      case 'online':
        return <Wifi className="w-4 h-4 text-green-400" />
      case 'offline':
        return <WifiOff className="w-4 h-4 text-red-400" />
      case 'connecting':
        return <RefreshCw className="w-4 h-4 text-yellow-400 animate-spin" />
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />
      default:
        return <WifiOff className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusColor = () => {
    switch (server.status) {
      case 'online':
        return 'border-green-500/30 bg-green-500/5'
      case 'offline':
        return 'border-red-500/30 bg-red-500/5'
      case 'connecting':
        return 'border-yellow-500/30 bg-yellow-500/5'
      case 'error':
        return 'border-red-500/30 bg-red-500/5'
      default:
        return 'border-gray-500/30'
    }
  }

  const formatLastSeen = (date?: Date) => {
    if (!date) return 'Never'
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    
    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`
    
    const days = Math.floor(hours / 24)
    return `${days}d ago`
  }

  return (
    <div
      className={clsx(
        'border-2 rounded-lg p-4 transition-all duration-200 cursor-pointer hover:border-cyan-500/50',
        getStatusColor(),
        isSelected 
          ? 'border-cyan-500 bg-cyan-500/10 shadow-lg shadow-cyan-500/20' 
          : 'border-gray-600 hover:bg-gray-700/30'
      )}
      onClick={onSelect}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <Server className="w-5 h-5 text-gray-400" />
          <div>
            <h3 className="font-semibold text-lg">{server.name}</h3>
            <p className="text-gray-400 text-sm">{server.description}</p>
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation()
            onRefresh()
          }}
          className="p-1.5 rounded-md hover:bg-gray-600 transition-colors"
          disabled={server.status === 'connecting'}
        >
          <RefreshCw 
            className={clsx(
              'w-4 h-4 text-gray-400', 
              server.status === 'connecting' && 'animate-spin'
            )} 
          />
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-3">
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <span className={clsx(
            'text-sm font-medium capitalize',
            server.status === 'online' && 'text-green-400',
            server.status === 'offline' && 'text-red-400',
            server.status === 'connecting' && 'text-yellow-400',
            server.status === 'error' && 'text-red-400'
          )}>
            {server.status}
          </span>
        </div>
        
        <div className="flex items-center gap-2 text-gray-400">
          <Clock className="w-3 h-3" />
          <span className="text-sm">{formatLastSeen(server.lastSeen)}</span>
        </div>
      </div>

      <div className="flex items-center justify-between text-sm">
        <div className="text-gray-400">
          <span className="text-gray-500">Host:</span> {server.host}
        </div>
        <div className="text-gray-400">
          <span className="text-gray-500">Tools:</span> {server.tools.length}
        </div>
      </div>

      {server.metrics && server.status === 'online' && (
        <div className="mt-3 pt-3 border-t border-gray-700 grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-xs text-gray-500">Uptime</div>
            <div className="text-sm font-medium text-green-400">{server.metrics.uptime}</div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-500">Requests</div>
            <div className="text-sm font-medium">{server.metrics.requests.toLocaleString()}</div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-500">Errors</div>
            <div className={clsx(
              'text-sm font-medium',
              server.metrics.errors > 0 ? 'text-red-400' : 'text-green-400'
            )}>
              {server.metrics.errors}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}