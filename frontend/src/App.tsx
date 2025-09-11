import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AppShell } from './components/AppShell';
import { HomePage } from './pages/HomePage';
import { CanvasPage } from './pages/CanvasPage';
import { LibraryPage } from './pages/LibraryPage';
import { PluginsPage } from './pages/PluginsPage';
import { SettingsPage } from './pages/SettingsPage';

function App() {
  return (
    <div className="min-h-screen bg-gradient-midnight text-midnight-100">
      <AppShell>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/canvas/:id?" element={<CanvasPage />} />
          <Route path="/library" element={<LibraryPage />} />
          <Route path="/plugins" element={<PluginsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </AppShell>
    </div>
  );
}

export default App;