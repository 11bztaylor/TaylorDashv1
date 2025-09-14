import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Layout } from './Layout';
import { UserManagement } from './UserManagement';
import { LogViewer } from './LogViewer';

export const SettingsView: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('settings');

  return (
    <Layout title="Settings">
      <div className="pb-16">
        {/* Tab navigation */}
        <div className="mb-6">
          <div className="flex space-x-1 bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('settings')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'settings'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:text-white hover:bg-gray-700'
              }`}
            >
              System Settings
            </button>
            {user?.role === 'admin' && (
              <button
                onClick={() => setActiveTab('users')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'users'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:text-white hover:bg-gray-700'
                }`}
              >
                User Management
              </button>
            )}
            <button
              onClick={() => setActiveTab('logs')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'logs'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:text-white hover:bg-gray-700'
              }`}
            >
              System Logs
            </button>
          </div>
        </div>

        {/* Tab content */}
        {activeTab === 'settings' ? (
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">System Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  API Endpoint
                </label>
                <input
                  type="text"
                  defaultValue="/api"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  readOnly
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Theme
                </label>
                <select className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white">
                  <option>Dark</option>
                  <option>Light</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Auto-refresh Interval
                </label>
                <select className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white">
                  <option value="5">5 seconds</option>
                  <option value="10">10 seconds</option>
                  <option value="30">30 seconds</option>
                  <option value="60">1 minute</option>
                </select>
              </div>
            </div>
          </div>
        ) : activeTab === 'users' && user?.role === 'admin' ? (
          <UserManagement />
        ) : (
          <LogViewer />
        )}
      </div>
    </Layout>
  );
};