import React from 'react';
import { BookOpen, Download, Star, Clock } from 'lucide-react';

export const Library: React.FC = () => {
  const libraryItems = [
    {
      id: '1',
      title: 'System Monitoring Dashboard',
      description: 'Real-time system performance metrics with alerts',
      category: 'Templates',
      downloads: 1420,
      rating: 4.8,
      lastUpdated: '2 days ago'
    },
    {
      id: '2',
      title: 'Project Status Grid',
      description: 'Multi-project overview with progress tracking',
      category: 'Widgets',
      downloads: 890,
      rating: 4.6,
      lastUpdated: '1 week ago'
    },
    {
      id: '3',
      title: 'Analytics Widgets Pack',
      description: 'Collection of data visualization components',
      category: 'Widget Packs',
      downloads: 2100,
      rating: 4.9,
      lastUpdated: '3 days ago'
    },
    {
      id: '4',
      title: 'Dark Theme Preset',
      description: 'Midnight cyber aesthetic theme configuration',
      category: 'Themes',
      downloads: 3200,
      rating: 4.7,
      lastUpdated: '5 days ago'
    }
  ];

  const categories = ['All', 'Templates', 'Widgets', 'Widget Packs', 'Themes'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900/50 via-black/50 to-gray-900/50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-2">Widget Library</h2>
          <p className="text-gray-400">Discover and download dashboard components</p>
        </div>

        {/* Categories */}
        <div className="flex space-x-4 mb-6 overflow-x-auto">
          {categories.map((category) => (
            <button
              key={category}
              className="px-4 py-2 bg-black/30 backdrop-blur-sm border border-gray-700/50 rounded-lg text-gray-300 hover:text-white hover:border-cyan-500/30 transition-colors whitespace-nowrap"
            >
              {category}
            </button>
          ))}
        </div>

        {/* Library Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {libraryItems.map((item) => (
            <div
              key={item.id}
              className="bg-black/40 backdrop-blur-sm border border-gray-700/50 rounded-lg p-6 hover:border-cyan-500/30 transition-colors group"
            >
              <div className="flex items-start justify-between mb-4">
                <BookOpen className="w-6 h-6 text-cyan-400" />
                <span className="text-xs px-2 py-1 bg-cyan-500/20 text-cyan-300 rounded">
                  {item.category}
                </span>
              </div>

              <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-cyan-300 transition-colors">
                {item.title}
              </h3>
              <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                {item.description}
              </p>

              <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-1">
                    <Download className="w-3 h-3" />
                    <span>{item.downloads.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Star className="w-3 h-3 text-yellow-400" />
                    <span>{item.rating}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-1">
                  <Clock className="w-3 h-3" />
                  <span>{item.lastUpdated}</span>
                </div>
              </div>

              <button className="w-full py-2 bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/30 rounded-lg text-cyan-300 hover:text-white transition-colors">
                Add to Dashboard
              </button>
            </div>
          ))}
        </div>

        {/* Featured Section */}
        <div className="mt-12">
          <h3 className="text-xl font-bold text-white mb-6">Featured Collections</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border border-cyan-500/30 rounded-lg p-6">
              <h4 className="text-lg font-semibold text-cyan-300 mb-2">DevOps Essentials</h4>
              <p className="text-gray-400 text-sm mb-4">
                Complete dashboard setup for development and operations monitoring
              </p>
              <button className="text-cyan-300 hover:text-white text-sm font-medium">
                Explore Collection →
              </button>
            </div>
            <div className="bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-500/30 rounded-lg p-6">
              <h4 className="text-lg font-semibold text-orange-300 mb-2">Analytics Pro</h4>
              <p className="text-gray-400 text-sm mb-4">
                Advanced visualization widgets for data analysis and reporting
              </p>
              <button className="text-orange-300 hover:text-white text-sm font-medium">
                Explore Collection →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};