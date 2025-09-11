import { NavLink } from 'react-router-dom';
import { T } from '../lib/tokens';

export function Nav() {
  return (
    <nav className={`${T.card} border-b border-slate-700`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* TaylorDash Logo/Brand */}
          <div className="flex items-center">
            <h1 className="text-xl font-bold bg-gradient-to-r from-[#355E3B] via-[#2f4f1d] to-[#FF6600] bg-clip-text text-transparent">
              TaylorDash
            </h1>
          </div>

          {/* Navigation Tabs */}
          <div className="flex space-x-1">
            <NavLink
              to="/status"
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-xl text-sm hover:bg-white/10 transition-colors ${
                  isActive ? 'bg-white/20 text-white' : 'text-slate-300'
                }`
              }
            >
              Status
            </NavLink>
            <NavLink
              to="/canvas"
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-xl text-sm hover:bg-white/10 transition-colors ${
                  isActive ? 'bg-white/20 text-white' : 'text-slate-300'
                }`
              }
            >
              Canvas
            </NavLink>
            <NavLink
              to="/projects"
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-xl text-sm hover:bg-white/10 transition-colors ${
                  isActive ? 'bg-white/20 text-white' : 'text-slate-300'
                }`
              }
            >
              Projects
            </NavLink>
            <NavLink
              to="/plugins"
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-xl text-sm hover:bg-white/10 transition-colors ${
                  isActive ? 'bg-white/20 text-white' : 'text-slate-300'
                }`
              }
            >
              Plugins
            </NavLink>
          </div>
        </div>
      </div>
    </nav>
  );
}