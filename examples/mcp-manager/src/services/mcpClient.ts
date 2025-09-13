import { MCPServer, MCPTool } from '../App';

// MCP Protocol Message Types
interface MCPRequest {
  jsonrpc: '2.0';
  id: string | number;
  method: string;
  params?: any;
}

interface MCPResponse {
  jsonrpc: '2.0';
  id: string | number;
  result?: any;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}

interface MCPListToolsResponse {
  tools: Array<{
    name: string;
    description: string;
    inputSchema: {
      type: 'object';
      properties: Record<string, any>;
      required?: string[];
    };
  }>;
}

interface MCPCallToolResponse {
  content: Array<{
    type: 'text';
    text: string;
  }>;
  isError?: boolean;
}

// MCP Server Configuration
interface MCPServerConfig {
  id: string;
  name: string;
  description: string;
  endpoint: string;
  type: 'stdio' | 'sse' | 'websocket';
  status: 'online' | 'offline' | 'connecting' | 'error';
}

class MCPClient {
  private serverConfigs: MCPServerConfig[] = [
    {
      id: 'homelab-mcp',
      name: 'Home Lab MCP',
      description: 'MCP server for managing home lab infrastructure',
      endpoint: '/api/mcp/homelab',
      type: 'stdio',
      status: 'offline'
    },
    {
      id: 'unifi-network-mcp', 
      name: 'UniFi Network MCP',
      description: 'UniFi Controller integration for network management',
      endpoint: '/api/mcp/unifi',
      type: 'stdio', 
      status: 'offline'
    }
  ];

  private requestId = 0;
  private activeConnections = new Map<string, boolean>();

  /**
   * Get authentication headers for API requests
   */
  private getAuthHeaders(): Record<string, string> {
    const sessionToken = localStorage.getItem('taylordash_session_token');
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    };
    
    if (sessionToken) {
      headers['Authorization'] = `Bearer ${sessionToken}`;
    }
    
    return headers;
  }

  /**
   * Discover available MCP servers by attempting connections
   */
  async discoverServers(): Promise<MCPServer[]> {
    console.log('[MCPClient] Starting server discovery...');
    
    const servers: MCPServer[] = [];
    
    for (const config of this.serverConfigs) {
      try {
        console.log(`[MCPClient] Checking server: ${config.name}`);
        
        // For stdio MCP servers, we need to use a backend proxy
        // since browsers can't spawn processes directly
        const server = await this.connectToServer(config);
        servers.push(server);
        
      } catch (error) {
        console.warn(`[MCPClient] Failed to connect to ${config.name}:`, error);
        
        // Add offline server to list
        servers.push({
          id: config.id,
          name: config.name,
          description: config.description,
          host: config.endpoint,
          status: 'offline',
          lastSeen: new Date(Date.now() - 900000), // 15 minutes ago
          tools: [],
          metrics: {
            uptime: '0m',
            requests: 0,
            errors: 1
          }
        });
      }
    }
    
    console.log(`[MCPClient] Discovery complete. Found ${servers.length} servers`);
    return servers;
  }

  /**
   * Connect to an MCP server and get its capabilities
   */
  private async connectToServer(config: MCPServerConfig): Promise<MCPServer> {
    console.log(`[MCPClient] Connecting to ${config.name}...`);
    
    // For now, we'll create a bridge through the TaylorDash backend
    // which can spawn the MCP server process and proxy stdio communication
    const response = await fetch('/api/v1/mcp/connect', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        serverId: config.id,
        endpoint: config.endpoint
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const connection = await response.json();
    
    // Get server capabilities using list_tools
    const tools = await this.listTools(config.id);
    
    // Get server metrics
    const metrics = await this.getServerMetrics(config.id);
    
    this.activeConnections.set(config.id, true);
    
    return {
      id: config.id,
      name: config.name,
      description: config.description,
      host: config.endpoint,
      status: 'online',
      lastSeen: new Date(),
      version: connection.version || '1.0.0',
      tools,
      metrics
    };
  }

  /**
   * List available tools from an MCP server
   */
  async listTools(serverId: string): Promise<MCPTool[]> {
    console.log(`[MCPClient] Listing tools for ${serverId}...`);
    
    const request: MCPRequest = {
      jsonrpc: '2.0',
      id: ++this.requestId,
      method: 'tools/list'
    };

    const response = await this.sendRequest(serverId, request);
    
    if (response.error) {
      console.error(`[MCPClient] Error listing tools:`, response.error);
      throw new Error(response.error.message);
    }

    const toolsResponse = response.result as MCPListToolsResponse;
    
    return toolsResponse.tools.map(tool => ({
      name: tool.name,
      description: tool.description,
      inputSchema: tool.inputSchema
    }));
  }

  /**
   * Execute a tool on an MCP server
   */
  async callTool(serverId: string, toolName: string, args: Record<string, any>): Promise<string> {
    console.log(`[MCPClient] Calling tool ${toolName} on ${serverId} with args:`, args);
    
    const request: MCPRequest = {
      jsonrpc: '2.0',
      id: ++this.requestId,
      method: 'tools/call',
      params: {
        name: toolName,
        arguments: args
      }
    };

    const response = await this.sendRequest(serverId, request);
    
    if (response.error) {
      console.error(`[MCPClient] Error calling tool:`, response.error);
      throw new Error(response.error.message);
    }

    const toolResponse = response.result as MCPCallToolResponse;
    
    if (toolResponse.isError) {
      throw new Error(toolResponse.content[0]?.text || 'Tool execution failed');
    }
    
    return toolResponse.content[0]?.text || 'Tool executed successfully';
  }

  /**
   * Send a request to an MCP server via the backend proxy
   */
  private async sendRequest(serverId: string, request: MCPRequest): Promise<MCPResponse> {
    const response = await fetch('/api/v1/mcp/request', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        serverId,
        request
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get server metrics and status
   */
  private async getServerMetrics(serverId: string): Promise<{ uptime: string; requests: number; errors: number }> {
    try {
      const response = await fetch(`/api/v1/mcp/metrics/${serverId}`, {
        headers: this.getAuthHeaders()
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.warn(`[MCPClient] Failed to get metrics for ${serverId}:`, error);
      return {
        uptime: 'Unknown',
        requests: 0,
        errors: 0
      };
    }
  }

  /**
   * Check server health status
   */
  async checkServerHealth(serverId: string): Promise<'online' | 'offline' | 'error'> {
    try {
      const response = await fetch(`/api/v1/mcp/health/${serverId}`, {
        headers: this.getAuthHeaders()
      });

      return response.ok ? 'online' : 'offline';
    } catch (error) {
      console.error(`[MCPClient] Health check failed for ${serverId}:`, error);
      return 'error';
    }
  }

  /**
   * Disconnect from an MCP server
   */
  async disconnectServer(serverId: string): Promise<void> {
    console.log(`[MCPClient] Disconnecting from ${serverId}...`);
    
    try {
      await fetch(`/api/v1/mcp/disconnect/${serverId}`, {
        method: 'POST',
        headers: this.getAuthHeaders()
      });
      
      this.activeConnections.delete(serverId);
    } catch (error) {
      console.error(`[MCPClient] Failed to disconnect from ${serverId}:`, error);
    }
  }
}

// Singleton instance
export const mcpClient = new MCPClient();
export default mcpClient;