import React, { useState } from 'react';
import { 
  User, 
  Palette, 
  Bell, 
  Shield, 
  Database,
  Monitor,
  Keyboard,
  Globe,
  Save,
  RefreshCw
} from 'lucide-react';
import { cn } from '@/utils';

export function SettingsPage() {
  const [selectedSection, setSelectedSection] = useState('general');

  const sections = [
    { id: 'general', label: 'General', icon: User },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'data', label: 'Data & Storage', icon: Database },
    { id: 'display', label: 'Display', icon: Monitor },
    { id: 'shortcuts', label: 'Shortcuts', icon: Keyboard },
    { id: 'advanced', label: 'Advanced', icon: Globe },
  ];

  const [settings, setSettings] = useState({
    // General
    username: 'Taylor',
    email: 'taylor@example.com',
    language: 'en',
    timezone: 'UTC-5',
    
    // Appearance
    theme: 'midnight',
    accentColor: 'cyber',
    fontSize: 'medium',
    compactMode: false,
    
    // Notifications
    pushNotifications: true,
    emailNotifications: false,
    soundEffects: true,
    systemNotifications: true,
    
    // Security
    twoFactorAuth: false,
    sessionTimeout: '30',
    autoLogout: true,
    
    // Data
    autoSave: true,
    backupFrequency: 'daily',
    dataRetention: '90',
    
    // Display
    gridSize: '20',
    snapToGrid: true,
    showMinimap: true,
    fullscreen: false,
    
    // Shortcuts
    enableShortcuts: true,
    
    // Advanced
    experimentalFeatures: false,
    debugMode: false,
    telemetry: true,
  });

  const updateSetting = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const renderGeneralSettings = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-midnight-300 mb-2">
            Display Name
          </label>
          <input
            type="text"
            value={settings.username}
            onChange={(e) => updateSetting('username', e.target.value)}
            className="input-cyber"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-midnight-300 mb-2">
            Email Address
          </label>
          <input
            type="email"
            value={settings.email}
            onChange={(e) => updateSetting('email', e.target.value)}
            className="input-cyber"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-midnight-300 mb-2">
            Language
          </label>
          <select
            value={settings.language}
            onChange={(e) => updateSetting('language', e.target.value)}
            className="input-cyber"
          >
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-midnight-300 mb-2">
            Timezone
          </label>
          <select
            value={settings.timezone}
            onChange={(e) => updateSetting('timezone', e.target.value)}
            className="input-cyber"
          >
            <option value="UTC-8">UTC-8 (Pacific)</option>
            <option value="UTC-5">UTC-5 (Eastern)</option>
            <option value="UTC+0">UTC+0 (GMT)</option>
            <option value="UTC+1">UTC+1 (CET)</option>
          </select>
        </div>
      </div>
    </div>
  );

  const renderAppearanceSettings = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-midnight-300 mb-2">
            Theme
          </label>
          <div className="grid grid-cols-2 gap-3">
            {['midnight', 'cyber'].map((theme) => (
              <button
                key={theme}
                onClick={() => updateSetting('theme', theme)}
                className={cn(
                  'p-4 rounded-lg border-2 transition-all',
                  settings.theme === theme
                    ? 'border-cyber-500 bg-cyber-500/10'
                    : 'border-midnight-700 hover:border-midnight-600'
                )}
              >
                <div className="text-sm font-medium text-midnight-100 capitalize">
                  {theme}
                </div>
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-midnight-300 mb-2">
            Accent Color
          </label>
          <div className="grid grid-cols-3 gap-2">
            {['cyber', 'orange', 'purple'].map((color) => (
              <button
                key={color}
                onClick={() => updateSetting('accentColor', color)}
                className={cn(
                  'w-full h-12 rounded-lg border-2 transition-all',
                  color === 'cyber' && 'bg-cyber-500',
                  color === 'orange' && 'bg-orange-500',
                  color === 'purple' && 'bg-purple-500',
                  settings.accentColor === color
                    ? 'border-white'
                    : 'border-midnight-700'
                )}
              />
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-midnight-300 mb-2">
            Font Size
          </label>
          <select
            value={settings.fontSize}
            onChange={(e) => updateSetting('fontSize', e.target.value)}
            className="input-cyber"
          >
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </select>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <label className="block text-sm font-medium text-midnight-300 mb-1">
              Compact Mode
            </label>
            <p className="text-xs text-midnight-400">
              Reduce spacing and padding
            </p>
          </div>
          <button
            onClick={() => updateSetting('compactMode', !settings.compactMode)}
            className={cn(
              'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
              settings.compactMode ? 'bg-cyber-500' : 'bg-midnight-700'
            )}
          >
            <span
              className={cn(
                'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                settings.compactMode ? 'translate-x-6' : 'translate-x-1'
              )}
            />
          </button>
        </div>
      </div>
    </div>
  );

  const renderSection = () => {
    switch (selectedSection) {
      case 'general':
        return renderGeneralSettings();
      case 'appearance':
        return renderAppearanceSettings();
      case 'notifications':
        return (
          <div className="space-y-4">
            {[
              { key: 'pushNotifications', label: 'Push Notifications', description: 'Receive push notifications' },
              { key: 'emailNotifications', label: 'Email Notifications', description: 'Receive email updates' },
              { key: 'soundEffects', label: 'Sound Effects', description: 'Play sounds for interactions' },
              { key: 'systemNotifications', label: 'System Notifications', description: 'Show system alerts' },
            ].map((item) => (
              <div key={item.key} className="flex items-center justify-between p-4 panel-midnight rounded-lg">
                <div>
                  <label className="block text-sm font-medium text-midnight-300 mb-1">
                    {item.label}
                  </label>
                  <p className="text-xs text-midnight-400">
                    {item.description}
                  </p>
                </div>
                <button
                  onClick={() => updateSetting(item.key, !settings[item.key as keyof typeof settings])}
                  className={cn(
                    'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                    settings[item.key as keyof typeof settings] ? 'bg-cyber-500' : 'bg-midnight-700'
                  )}
                >
                  <span
                    className={cn(
                      'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                      settings[item.key as keyof typeof settings] ? 'translate-x-6' : 'translate-x-1'
                    )}
                  />
                </button>
              </div>
            ))}
          </div>
        );
      default:
        return (
          <div className="flex items-center justify-center h-64 text-midnight-400">
            <div className="text-center">
              <div className="w-16 h-16 bg-midnight-700/50 rounded-full flex items-center justify-center mx-auto mb-4">
                <Globe className="w-8 h-8" />
              </div>
              <p>Settings for {selectedSection} are coming soon</p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="h-full flex">
      {/* Sidebar */}
      <div className="w-64 bg-midnight-900/50 backdrop-blur-sm border-r border-midnight-700/50">
        <div className="p-4">
          <h2 className="text-lg font-semibold text-midnight-100 mb-4">Settings</h2>
          <nav className="space-y-1">
            {sections.map((section) => {
              const Icon = section.icon;
              return (
                <button
                  key={section.id}
                  onClick={() => setSelectedSection(section.id)}
                  className={cn(
                    'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                    selectedSection === section.id
                      ? 'bg-cyber-500/20 text-cyber-300 border border-cyber-500/30'
                      : 'text-midnight-400 hover:text-midnight-300 hover:bg-midnight-700/50'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {section.label}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="h-16 border-b border-midnight-700/50 px-6 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-midnight-100 capitalize">
              {selectedSection} Settings
            </h1>
          </div>

          <div className="flex items-center gap-3">
            <button className="btn-cyber-outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Reset
            </button>
            <button className="btn-cyber">
              <Save className="w-4 h-4 mr-2" />
              Save Changes
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto scrollbar-cyber p-6">
          <div className="max-w-4xl">
            {renderSection()}
          </div>
        </div>
      </div>
    </div>
  );
}