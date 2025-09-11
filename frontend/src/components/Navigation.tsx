import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  Home, 
  Layout, 
  Library, 
  Puzzle, 
  Settings, 
  Terminal,
  Zap
} from 'lucide-react';
import { cn } from '@/utils';

const navigationItems = [
  { 
    id: 'home', 
    label: 'Home', 
    icon: Home, 
    path: '/' 
  },
  { 
    id: 'canvas', 
    label: 'Canvas', 
    icon: Layout, 
    path: '/canvas' 
  },
  { 
    id: 'library', 
    label: 'Library', 
    icon: Library, 
    path: '/library' 
  },
  { 
    id: 'plugins', 
    label: 'Plugins', 
    icon: Puzzle, 
    path: '/plugins' 
  },
  { 
    id: 'settings', 
    label: 'Settings', 
    icon: Settings, 
    path: '/settings' 
  },
];

export function Navigation() {
  const location = useLocation();

  return (
    <nav className="w-16 lg:w-64 bg-midnight-900/50 backdrop-blur-sm border-r border-midnight-700/50 flex flex-col">
      {/* Logo/Brand */}
      <div className="p-4 border-b border-midnight-700/50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-cyber rounded-lg flex items-center justify-center">
            <Terminal className="w-5 h-5 text-midnight-900" />
          </div>
          <div className="hidden lg:block">
            <h1 className="text-lg font-bold text-cyber-gradient">TaylorDash</h1>
            <p className="text-xs text-midnight-400">Visual Shell</p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 p-2">
        <ul className="space-y-1">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path || 
                           (item.path !== '/' && location.pathname.startsWith(item.path));
            
            return (
              <li key={item.id}>
                <NavLink
                  to={item.path}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200',
                    'hover:bg-midnight-700/50 hover:text-cyber-300',
                    'focus:outline-none focus:ring-2 focus:ring-cyber-500/50',
                    isActive 
                      ? 'bg-cyber-500/10 text-cyber-300 border border-cyber-500/30' 
                      : 'text-midnight-300'
                  )}
                >
                  <Icon className={cn(
                    'w-5 h-5 flex-shrink-0',
                    isActive ? 'text-cyber-400' : 'text-midnight-400'
                  )} />
                  <span className="hidden lg:block font-medium">
                    {item.label}
                  </span>
                  {isActive && (
                    <div className="hidden lg:block ml-auto">
                      <Zap className="w-3 h-3 text-cyber-400" />
                    </div>
                  )}
                </NavLink>
              </li>
            );
          })}
        </ul>
      </div>

      {/* User Profile / Quick Actions */}
      <div className="p-4 border-t border-midnight-700/50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-cyber rounded-full flex items-center justify-center">
            <span className="text-xs font-bold text-midnight-900">T</span>
          </div>
          <div className="hidden lg:block flex-1 min-w-0">
            <p className="text-sm font-medium text-midnight-200 truncate">Taylor</p>
            <p className="text-xs text-midnight-400 truncate">Developer</p>
          </div>
        </div>
      </div>
    </nav>
  );
}