import React from 'react';
import { Home, Library, Settings } from 'lucide-react';

interface AppShellProps {
  currentView: 'home' | 'library';
  onViewChange: (view: 'home' | 'library') => void;
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ 
  currentView, 
  onViewChange, 
  children 
}) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900">
      {/* Header */}
      <header className="border-b border-gray-700/50 bg-black/30 backdrop-blur-sm">
        <div className="px-6 py-4">
          <h1 className="text-4xl font-black tracking-tight bg-gradient-to-r from-[#355E3B] via-[#2f4f1d] to-[#FF6600] bg-clip-text text-transparent">
            MIDNIGHT HUD
          </h1>
          <p className="text-gray-400 text-sm mt-1">TaylorDash Visual Plugin</p>
        </div>
      </header>

      {/* Navigation */}
      <nav className="border-b border-gray-700/50 bg-black/20 backdrop-blur-sm">
        <div className="px-6 py-3">
          <div className="flex space-x-6">
            <button
              onClick={() => onViewChange('home')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                currentView === 'home'
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Home className="w-4 h-4" />
              <span>Home</span>
            </button>
            
            <button
              onClick={() => onViewChange('library')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                currentView === 'library'
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Library className="w-4 h-4" />
              <span>Library</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="relative overflow-hidden">
        {children}
      </main>
    </div>
  );
};