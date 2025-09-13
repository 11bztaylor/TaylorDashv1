import React, { useState, useEffect } from 'react';
import { ExternalLink, Maximize2, Minimize2, RefreshCw, Server, Shield } from 'lucide-react';

export const MCPManagerPage: React.FC = () => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [iframeKey, setIframeKey] = useState(0);

  // Simulate loading time
  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  const handleRefresh = () => {
    setIsLoading(true);
    setIframeKey(prev => prev + 1);
    setTimeout(() => setIsLoading(false), 500);
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const openInNewTab = () => {
    window.open('http://localhost:5174', '_blank');
  };

  return (
    <div className={`${isFullscreen ? 'fixed inset-0 z-50' : 'h-full'} bg-gray-900`}>
      {/* Plugin Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Server className="w-6 h-6 text-cyan-400" />
              <h1 className="text-xl font-semibold text-white">MCP Manager</h1>
              <div className="flex items-center gap-1 px-2 py-1 bg-orange-500/20 text-orange-400 rounded text-xs font-medium">
                <Shield className="w-3 h-3" />
                Admin Only
              </div>
            </div>
            <p className="text-sm text-gray-400">
              Model Context Protocol server management and monitoring • Version 0.1.0
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={handleRefresh}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
              title="Refresh Plugin"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            
            <button
              onClick={toggleFullscreen}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
              title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
            >
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>
            
            <button
              onClick={openInNewTab}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
              title="Open in New Tab"
            >
              <ExternalLink className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Plugin Content */}
      <div className="relative h-full bg-gray-900">
        {isLoading && (
          <div className="absolute inset-0 bg-gray-900 flex items-center justify-center z-10">
            <div className="text-center">
              <Server className="w-12 h-12 text-cyan-400 mx-auto mb-4 animate-pulse" />
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-cyan-400 mx-auto mb-4"></div>
              <p className="text-gray-400">Loading MCP Manager...</p>
              <p className="text-gray-500 text-sm mt-2">Discovering Model Context Protocol servers...</p>
            </div>
          </div>
        )}
        
        <iframe
          key={iframeKey}
          src="http://localhost:5174"
          className="w-full h-full border-0"
          title="MCP Manager Plugin"
          sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
          onLoad={() => setIsLoading(false)}
          onError={() => setIsLoading(false)}
        />
      </div>

      {/* Status Bar */}
      <div className="bg-gray-800 border-t border-gray-700 px-4 py-2">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-4">
            <span>Status: Active</span>
            <span>•</span>
            <span>Source: http://localhost:5174</span>
            <span>•</span>
            <span>Type: Integration Plugin</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
            <span>MCP Network Scanning</span>
          </div>
        </div>
      </div>
    </div>
  );
};