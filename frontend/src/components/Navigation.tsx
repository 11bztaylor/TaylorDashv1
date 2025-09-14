import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Folder, Settings, Layers, Plug } from 'lucide-react';

export const Navigation: React.FC = () => {
  const location = useLocation();
  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/projects', icon: Folder, label: 'Projects' },
    { path: '/flow', icon: Layers, label: 'Flow Canvas' },
    { path: '/plugins', icon: Plug, label: 'Plugins' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  // All navigation items are accessible to authenticated users
  const filteredNavItems = navItems;

  return (
    <nav className="bg-gray-800 border-b border-gray-700 px-6 py-2">
      <div className="flex space-x-6">
        {filteredNavItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:text-white hover:bg-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
};