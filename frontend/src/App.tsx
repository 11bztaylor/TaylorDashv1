import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Home, Folder, Settings, Layers } from 'lucide-react';

// Simple inline components to avoid import issues
const ConnectionStatus: React.FC<{ onConnectionChange: (connected: boolean) => void }> = ({ onConnectionChange }) => {
  const [isConnected, setIsConnected] = useState(false);
  
  React.useEffect(() => {
    // Simulate connection check
    const checkConnection = async () => {
      try {
        const response = await fetch('/api/v1/health/stack');
        const connected = response.ok;
        setIsConnected(connected);
        onConnectionChange(connected);
      } catch (error) {
        setIsConnected(false);
        onConnectionChange(false);
      }
    };
    
    checkConnection();
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, [onConnectionChange]);

  return (
    <div className="flex items-center space-x-2">
      <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
      <span className="text-sm text-gray-400">
        {isConnected ? 'Connected' : 'Disconnected'}
      </span>
    </div>
  );
};

const ProjectsList: React.FC = () => {
  const [projects, setProjects] = useState([]);

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-4">Projects</h2>
      <p className="text-gray-400 text-sm">
        {projects.length === 0 ? 'No projects yet. Start by creating your first project!' : `${projects.length} projects`}
      </p>
    </div>
  );
};

const FlowCanvas: React.FC = () => {
  return (
    <div className="bg-gray-800 rounded-lg p-6 h-64">
      <h2 className="text-xl font-semibold text-white mb-4">System Flow</h2>
      <div className="flex items-center justify-center h-full bg-gray-700 rounded">
        <p className="text-gray-400">Visual flow canvas coming soon...</p>
      </div>
    </div>
  );
};

// Layout wrapper component
const Layout: React.FC<{ children: React.ReactNode; title: string }> = ({ children, title }) => {
  const [isConnected, setIsConnected] = useState<boolean>(false);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-white">TaylorDash</h1>
            <span className="text-sm text-gray-400">{title}</span>
          </div>
          <ConnectionStatus onConnectionChange={setIsConnected} />
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {children}
      </main>

      {/* Status Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-gray-800 border-t border-gray-700 px-6 py-2">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <div className="flex items-center space-x-4">
            <span>Backend Status: {isConnected ? 'Connected' : 'Disconnected'}</span>
            <span>•</span>
            <span>API Endpoint: /api</span>
            <span>•</span>
            <span>Version: 1.0.0</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
            <span>System Health</span>
          </div>
        </div>
      </div>
    </div>
  );
};

const Dashboard: React.FC = () => {
  return (
    <Layout title="Dashboard">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pb-16">
        {/* Projects Section */}
        <div className="space-y-6">
          <ProjectsList />
        </div>

        {/* Canvas Section */}
        <div className="space-y-6">
          <FlowCanvas />
        </div>
      </div>
    </Layout>
  );
};

const ProjectsPage: React.FC = () => {
  return (
    <Layout title="Project Management">
      <div className="pb-16">
        <div className="mb-6">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
            + New Project
          </button>
        </div>
        <ProjectsList />
      </div>
    </Layout>
  );
};

const FlowPage: React.FC = () => {
  return (
    <Layout title="Flow Canvas">
      <div className="pb-16 h-screen">
        <FlowCanvas />
      </div>
    </Layout>
  );
};

const SettingsPage: React.FC = () => {
  return (
    <Layout title="Settings">
      <div className="pb-16">
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
          </div>
        </div>
      </div>
    </Layout>
  );
};

const Navigation: React.FC = () => {
  const location = useLocation();
  
  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/projects', icon: Folder, label: 'Projects' },
    { path: '/flow', icon: Layers, label: 'Flow Canvas' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <nav className="bg-gray-800 border-b border-gray-700 px-6 py-2">
      <div className="flex space-x-6">
        {navItems.map((item) => {
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

const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gray-900">
        <Navigation />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/flow" element={<FlowPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;