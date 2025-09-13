import React, { useState, useEffect } from 'react'
import { Server, Activity, Wifi, WifiOff, Settings, Terminal, AlertCircle, CheckCircle, Clock } from 'lucide-react'
import { MCPServerCard } from './components/MCPServerCard'
import { MCPConnectionStatus } from './components/MCPConnectionStatus'
import { MCPToolsPanel } from './components/MCPToolsPanel'
import mcpClient from './services/mcpClient'

export interface MCPServer {
  id: string
  name: string
  description: string
  host: string
  status: 'online' | 'offline' | 'connecting' | 'error'
  lastSeen?: Date
  version?: string
  tools: MCPTool[]
  metrics?: {
    uptime: string
    requests: number
    errors: number
  }
}

export interface MCPTool {
  name: string
  description: string
  inputSchema: any
  lastUsed?: Date
}

function App() {
  const [servers, setServers] = useState<MCPServer[]>([])
  const [selectedServer, setSelectedServer] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  // Real MCP server discovery and status checking
  useEffect(() => {
    const abortController = new AbortController()
    
    const discoverServers = async () => {
      setLoading(true)
      console.log('[App] Starting MCP server discovery...')
      
      try {
        // Use real MCP client to discover servers
        const discoveredServers = await mcpClient.discoverServers()
        
        // Check if component was unmounted
        if (abortController.signal.aborted) return
        
        console.log('[App] Discovered servers:', discoveredServers)
        setServers(discoveredServers)
      } catch (error) {
        // Check if component was unmounted
        if (abortController.signal.aborted) return
        
        console.error('[App] Server discovery failed:', error)
        
        // Fallback: Show error state
        setServers([{
          id: 'discovery-error',
          name: 'Discovery Failed',
          description: 'Unable to discover MCP servers. Check backend connection.',
          host: 'localhost',
          status: 'error',
          lastSeen: new Date(),
          tools: [],
          metrics: {
            uptime: '0m',
            requests: 0,
            errors: 1
          }
        }])
      } finally {
        if (!abortController.signal.aborted) {
          setLoading(false)
        }
      }
    }

    discoverServers()

    // Set up periodic health checks every 30 seconds
    const healthCheckInterval = setInterval(async () => {
      if (abortController.signal.aborted) return
      
      setServers(prevServers => 
        prevServers.map(server => ({
          ...server,
          status: 'connecting' as const
        }))
      )

      try {
        const updatedServers = await mcpClient.discoverServers()
        
        // Check if component was unmounted
        if (abortController.signal.aborted) return
        
        setServers(updatedServers)
      } catch (error) {
        // Check if component was unmounted
        if (abortController.signal.aborted) return
        
        console.error('[App] Health check failed:', error)
        // Mark servers as offline if health check fails
        setServers(prevServers => 
          prevServers.map(server => 
            server.id !== 'discovery-error' 
              ? { ...server, status: 'offline' as const }
              : server
          )
        )
      }
    }, 30000)

    return () => {
      abortController.abort()
      clearInterval(healthCheckInterval)
    }
  }, [])

  const handleServerRefresh = async (serverId: string) => {
    console.log(`[App] Refreshing server: ${serverId}`)
    
    setServers(prev => prev.map(server => 
      server.id === serverId 
        ? { ...server, status: 'connecting' as const }
        : server
    ))

    try {
      // Check individual server health
      const status = await mcpClient.checkServerHealth(serverId)
      
      setServers(prev => prev.map(server => 
        server.id === serverId 
          ? { 
              ...server, 
              status,
              lastSeen: new Date()
            }
          : server
      ))
      
      console.log(`[App] Server ${serverId} status: ${status}`)
    } catch (error) {
      console.error(`[App] Failed to refresh server ${serverId}:`, error)
      
      setServers(prev => prev.map(server => 
        server.id === serverId 
          ? { ...server, status: 'error' as const }
          : server
      ))
    }
  }

  const selectedServerData = selectedServer 
    ? servers.find(s => s.id === selectedServer) 
    : null

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto mb-4"></div>
          <p className="text-gray-300">Discovering MCP servers...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Server className="w-8 h-8 text-cyan-400" />
            <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
              MCP Manager
            </h1>
          </div>
          <p className="text-gray-400">
            Manage and monitor Model Context Protocol servers in your homelab
          </p>
        </div>

        {/* Connection Status Overview */}
        <MCPConnectionStatus servers={servers} />

        {/* Main Content */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Server List */}
          <div className="lg:col-span-2">
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5 text-cyan-400" />
                MCP Servers
              </h2>
              <div className="space-y-4">
                {servers.map(server => (
                  <MCPServerCard
                    key={server.id}
                    server={server}
                    isSelected={selectedServer === server.id}
                    onSelect={() => setSelectedServer(server.id)}
                    onRefresh={() => handleServerRefresh(server.id)}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Server Details Panel */}
          <div className="lg:col-span-1">
            {selectedServerData ? (
              <MCPToolsPanel server={selectedServerData} />
            ) : (
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <div className="text-center text-gray-400">
                  <Settings className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>Select an MCP server to view details and available tools</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App