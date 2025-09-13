import React, { useState, useEffect } from 'react'
import { Terminal, Play, Code, Clock, ArrowRight, Settings } from 'lucide-react'
import { MCPServer, MCPTool } from '../App'
import { clsx } from 'clsx'
import mcpClient from '../services/mcpClient'

interface MCPToolsPanelProps {
  server: MCPServer
}

interface ToolExecution {
  toolName: string
  args: Record<string, any>
  result?: string
  error?: string
  timestamp: Date
}

export const MCPToolsPanel: React.FC<MCPToolsPanelProps> = ({ server }) => {
  const [selectedTool, setSelectedTool] = useState<MCPTool | null>(null)
  const [toolArgs, setToolArgs] = useState<Record<string, any>>({})
  const [executions, setExecutions] = useState<ToolExecution[]>([])
  const [isExecuting, setIsExecuting] = useState(false)

  // Reset state when server changes to prevent memory leaks and stale data
  useEffect(() => {
    setSelectedTool(null)
    setToolArgs({})
    setExecutions([])
    setIsExecuting(false)
  }, [server.id])

  const executeTool = async () => {
    if (!selectedTool) return

    console.log(`[MCPToolsPanel] Executing tool: ${selectedTool.name} on server: ${server.id}`)
    
    setIsExecuting(true)
    const execution: ToolExecution = {
      toolName: selectedTool.name,
      args: toolArgs,
      timestamp: new Date()
    }

    try {
      // Use real MCP client to execute the tool
      const result = await mcpClient.callTool(server.id, selectedTool.name, toolArgs)
      console.log(`[MCPToolsPanel] Tool execution result:`, result)
      
      execution.result = result
      
      // Update last used timestamp for the tool
      selectedTool.lastUsed = new Date()
      
    } catch (error) {
      console.error(`[MCPToolsPanel] Tool execution failed:`, error)
      execution.error = error instanceof Error ? error.message : 'Unknown error occurred'
    }

    setExecutions(prev => {
      const newExecutions = [execution, ...prev]
      // Keep only the last 10 executions to prevent memory leaks
      return newExecutions.slice(0, 10)
    })
    setIsExecuting(false)
  }

  const renderArgInput = (propName: string, schema: any) => {
    const value = toolArgs[propName] || ''
    
    return (
      <div key={propName} className="mb-3">
        <label className="block text-sm font-medium text-gray-300 mb-1">
          {propName}
          {selectedTool?.inputSchema.required?.includes(propName) && (
            <span className="text-red-400 ml-1">*</span>
          )}
        </label>
        <input
          type={schema.type === 'number' ? 'number' : 'text'}
          value={value}
          onChange={(e) => setToolArgs(prev => ({
            ...prev,
            [propName]: schema.type === 'number' ? Number(e.target.value) : e.target.value
          }))}
          placeholder={schema.description || `Enter ${propName}...`}
          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:border-cyan-400 focus:outline-none"
        />
        {schema.description && (
          <p className="text-xs text-gray-500 mt-1">{schema.description}</p>
        )}
      </div>
    )
  }

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    })
  }

  return (
    <div className="space-y-6">
      {/* Server Info */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <div className="flex items-center gap-3 mb-4">
          <Settings className="w-5 h-5 text-cyan-400" />
          <h3 className="text-lg font-semibold">Server Details</h3>
        </div>
        
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-400">Name:</span>
            <span>{server.name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Host:</span>
            <span className="font-mono">{server.host}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Version:</span>
            <span>{server.version || 'Unknown'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Tools:</span>
            <span>{server.tools.length}</span>
          </div>
        </div>
      </div>

      {/* Tools List */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Terminal className="w-5 h-5 text-cyan-400" />
          Available Tools
        </h3>
        
        <div className="space-y-2">
          {server.tools.map((tool) => (
            <div
              key={tool.name}
              className={clsx(
                'p-3 rounded-md border cursor-pointer transition-all',
                selectedTool?.name === tool.name
                  ? 'border-cyan-500 bg-cyan-500/10'
                  : 'border-gray-600 hover:border-gray-500 hover:bg-gray-700/50'
              )}
              onClick={() => {
                setSelectedTool(tool)
                setToolArgs({})
              }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">{tool.name}</div>
                  <div className="text-sm text-gray-400">{tool.description}</div>
                </div>
                {tool.lastUsed && (
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <Clock className="w-3 h-3" />
                    {formatTimestamp(tool.lastUsed)}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tool Execution */}
      {selectedTool && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Play className="w-5 h-5 text-cyan-400" />
            Execute: {selectedTool.name}
          </h3>

          {/* Tool Arguments */}
          {selectedTool.inputSchema.properties && Object.keys(selectedTool.inputSchema.properties).length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-300 mb-3">Parameters</h4>
              {Object.entries(selectedTool.inputSchema.properties).map(([propName, schema]: [string, any]) =>
                renderArgInput(propName, schema)
              )}
            </div>
          )}

          {/* Execute Button */}
          <button
            onClick={executeTool}
            disabled={isExecuting}
            className={clsx(
              'w-full py-2 px-4 rounded-md font-medium transition-all',
              isExecuting
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-cyan-500 hover:bg-cyan-600 text-white'
            )}
          >
            {isExecuting ? 'Executing...' : 'Execute Tool'}
          </button>
        </div>
      )}

      {/* Execution History */}
      {executions.length > 0 && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Code className="w-5 h-5 text-cyan-400" />
            Execution History
          </h3>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {executions.map((execution, index) => (
              <div key={index} className="border border-gray-700 rounded-md p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-sm font-medium">{execution.toolName}</span>
                  <span className="text-xs text-gray-500">{formatTimestamp(execution.timestamp)}</span>
                </div>
                
                {Object.keys(execution.args).length > 0 && (
                  <div className="mb-2">
                    <div className="text-xs text-gray-400 mb-1">Arguments:</div>
                    <pre className="text-xs bg-gray-900 p-2 rounded overflow-x-auto">
                      {JSON.stringify(execution.args, null, 2)}
                    </pre>
                  </div>
                )}
                
                {execution.result && (
                  <div>
                    <div className="text-xs text-green-400 mb-1">Result:</div>
                    <pre className="text-xs bg-gray-900 p-2 rounded overflow-x-auto whitespace-pre-wrap">
                      {execution.result}
                    </pre>
                  </div>
                )}
                
                {execution.error && (
                  <div>
                    <div className="text-xs text-red-400 mb-1">Error:</div>
                    <pre className="text-xs bg-red-900/20 p-2 rounded overflow-x-auto">
                      {execution.error}
                    </pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}