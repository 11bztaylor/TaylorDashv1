import { Routes, Route, Navigate } from 'react-router-dom';
import { Nav } from './Nav';
import { T } from '../lib/tokens';
import { Status } from './routes/Status';
import { Canvas } from './routes/Canvas';
import Plugins from './routes/Plugins';
import { MidnightHudPage } from '../pages/plugins/MidnightHudPage';

const ProjectsPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold mb-4">Projects</h1>
    <p className="text-slate-300">Manage and organize your projects</p>
  </div>
);


function App() {
  return (
    <div className={`min-h-screen ${T.bg} ${T.text}`}>
      <Nav />
      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/status" replace />} />
          <Route path="/status" element={<Status />} />
          <Route path="/canvas" element={<Canvas />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/plugins" element={<Plugins />} />
          <Route path="/plugins/midnight-hud" element={<MidnightHudPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;