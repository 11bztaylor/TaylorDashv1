import React from 'react';
import { useParams } from 'react-router-dom';
import { 
  Play, 
  Pause, 
  Square, 
  Save, 
  Share, 
  Settings,
  Maximize2,
  Grid3X3,
  ZoomIn,
  ZoomOut
} from 'lucide-react';
import { cn } from '@/utils';

export function CanvasPage() {
  const { id } = useParams();
  const isNewCanvas = id === 'new' || !id;

  return (
    <div className="h-full flex flex-col">
      {/* Canvas Toolbar */}
      <div className="h-14 bg-midnight-900/50 backdrop-blur-sm border-b border-midnight-700/50 px-4 flex items-center justify-between">
        {/* Left side - Canvas controls */}
        <div className="flex items-center gap-2">
          <button className="btn-cyber-outline px-3 py-1 text-sm">
            <Play className="w-4 h-4" />
          </button>
          <button className="btn-cyber-outline px-3 py-1 text-sm">
            <Pause className="w-4 h-4" />
          </button>
          <button className="btn-cyber-outline px-3 py-1 text-sm">
            <Square className="w-4 h-4" />
          </button>
          
          <div className="w-px h-6 bg-midnight-700 mx-2" />
          
          <button className="btn-cyber-outline px-3 py-1 text-sm">
            <Save className="w-4 h-4" />
          </button>
          <button className="btn-cyber-outline px-3 py-1 text-sm">
            <Share className="w-4 h-4" />
          </button>
        </div>

        {/* Center - Canvas name */}
        <div className="flex-1 max-w-md mx-4">
          <input
            type="text"
            defaultValue={isNewCanvas ? 'Untitled Canvas' : 'Development Dashboard'}
            className="input-cyber text-center text-lg font-semibold"
          />
        </div>

        {/* Right side - View controls */}
        <div className="flex items-center gap-2">
          <button className="btn-cyber-outline px-3 py-1 text-sm">
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-sm text-midnight-300 font-mono min-w-[60px] text-center">
            100%
          </span>
          <button className="btn-cyber-outline px-3 py-1 text-sm">
            <ZoomIn className="w-4 h-4" />
          </button>
          
          <div className="w-px h-6 bg-midnight-700 mx-2" />
          
          <button className="btn-cyber-outline px-3 py-1 text-sm">
            <Grid3X3 className="w-4 h-4" />
          </button>
          <button className="btn-cyber-outline px-3 py-1 text-sm">
            <Maximize2 className="w-4 h-4" />
          </button>
          <button className="btn-cyber-outline px-3 py-1 text-sm">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Canvas Area */}
      <div className="flex-1 relative bg-midnight-950/50">
        {/* Grid Background */}
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `
              linear-gradient(rgba(0, 255, 65, 0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(0, 255, 65, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '20px 20px'
          }}
        />

        {/* Canvas Content */}
        <div className="relative h-full overflow-hidden">
          {isNewCanvas ? (
            // Empty canvas state
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-6 max-w-md">
                <div className="w-24 h-24 bg-gradient-cyber rounded-2xl flex items-center justify-center mx-auto">
                  <Grid3X3 className="w-12 h-12 text-midnight-900" />
                </div>
                
                <div className="space-y-2">
                  <h2 className="text-2xl font-bold text-midnight-100">
                    Welcome to your new canvas
                  </h2>
                  <p className="text-midnight-400">
                    Drag and drop widgets from the library to get started, or choose from our templates.
                  </p>
                </div>

                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <button className="btn-cyber">
                    Add Widget
                  </button>
                  <button className="btn-cyber-outline">
                    Browse Templates
                  </button>
                </div>
              </div>
            </div>
          ) : (
            // Canvas with widgets (placeholder)
            <div className="p-8">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Example widget placeholders */}
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <div
                    key={i}
                    className={cn(
                      'panel-cyber p-6 rounded-xl h-48 flex items-center justify-center',
                      'border-dashed border-cyber-500/30 hover:border-cyber-500/50 transition-colors',
                      'cursor-pointer group'
                    )}
                  >
                    <div className="text-center space-y-2">
                      <div className="w-12 h-12 bg-cyber-500/20 rounded-lg flex items-center justify-center mx-auto group-hover:bg-cyber-500/30 transition-colors">
                        <Grid3X3 className="w-6 h-6 text-cyber-400" />
                      </div>
                      <p className="text-sm text-midnight-400 group-hover:text-midnight-300 transition-colors">
                        Widget {i}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Canvas Minimap (bottom right) */}
        <div className="absolute bottom-4 right-4 w-48 h-32 panel-midnight rounded-lg p-2">
          <div className="w-full h-full bg-midnight-800/50 rounded border border-midnight-600 relative">
            <div className="absolute top-1 left-1 right-1 bottom-1 border border-cyber-500/50 rounded"></div>
            <div className="absolute top-2 left-2 text-xs text-midnight-400">Minimap</div>
          </div>
        </div>
      </div>
    </div>
  );
}