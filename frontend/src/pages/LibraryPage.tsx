import React, { useState } from 'react';
import { 
  Search, 
  Filter, 
  Grid3X3, 
  List, 
  Download,
  Star,
  Clock,
  Tag
} from 'lucide-react';
import { cn } from '@/utils';

export function LibraryPage() {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', label: 'All', count: 24 },
    { id: 'widgets', label: 'Widgets', count: 12 },
    { id: 'templates', label: 'Templates', count: 8 },
    { id: 'themes', label: 'Themes', count: 4 },
  ];

  const libraryItems = [
    {
      id: '1',
      name: 'System Monitor Widget',
      category: 'widgets',
      description: 'Real-time system performance monitoring with CPU, memory, and disk usage.',
      author: 'TaylorDash Team',
      version: '1.2.0',
      downloads: 1234,
      rating: 4.8,
      tags: ['monitoring', 'system', 'performance'],
      lastUpdated: '2 days ago',
      featured: true
    },
    {
      id: '2',
      name: 'Development Dashboard',
      category: 'templates',
      description: 'Complete dashboard template for software development workflows.',
      author: 'DevTools Pro',
      version: '2.1.0',
      downloads: 856,
      rating: 4.9,
      tags: ['development', 'dashboard', 'workflow'],
      lastUpdated: '1 week ago',
      featured: true
    },
    {
      id: '3',
      name: 'Network Status Widget',
      category: 'widgets',
      description: 'Monitor network connectivity and bandwidth usage in real-time.',
      author: 'NetworkTools',
      version: '1.0.5',
      downloads: 432,
      rating: 4.5,
      tags: ['network', 'connectivity', 'monitoring'],
      lastUpdated: '3 days ago',
      featured: false
    },
    {
      id: '4',
      name: 'Cyber Theme Pack',
      category: 'themes',
      description: 'Futuristic cyber-punk theme with neon accents and dark aesthetics.',
      author: 'ThemeForge',
      version: '1.1.2',
      downloads: 678,
      rating: 4.7,
      tags: ['theme', 'cyberpunk', 'neon'],
      lastUpdated: '5 days ago',
      featured: false
    },
    {
      id: '5',
      name: 'Project Timeline Widget',
      category: 'widgets',
      description: 'Visualize project milestones and deadlines with an interactive timeline.',
      author: 'ProjectPro',
      version: '1.3.1',
      downloads: 321,
      rating: 4.6,
      tags: ['project', 'timeline', 'planning'],
      lastUpdated: '1 day ago',
      featured: false
    },
    {
      id: '6',
      name: 'Minimal Dashboard',
      category: 'templates',
      description: 'Clean and minimal dashboard template focused on essential metrics.',
      author: 'MinimalDesign',
      version: '1.0.0',
      downloads: 789,
      rating: 4.4,
      tags: ['minimal', 'clean', 'dashboard'],
      lastUpdated: '2 weeks ago',
      featured: false
    }
  ];

  const filteredItems = libraryItems.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="h-full flex">
      {/* Sidebar */}
      <div className="w-64 bg-midnight-900/50 backdrop-blur-sm border-r border-midnight-700/50 p-4">
        {/* Search */}
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-midnight-400" />
          <input
            type="text"
            placeholder="Search library..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-cyber pl-10"
          />
        </div>

        {/* Categories */}
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-midnight-300 uppercase tracking-wider">
            Categories
          </h3>
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={cn(
                'w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors',
                selectedCategory === category.id
                  ? 'bg-cyber-500/20 text-cyber-300 border border-cyber-500/30'
                  : 'text-midnight-400 hover:text-midnight-300 hover:bg-midnight-700/50'
              )}
            >
              <span>{category.label}</span>
              <span className={cn(
                'text-xs px-2 py-0.5 rounded-full',
                selectedCategory === category.id
                  ? 'bg-cyber-500/30 text-cyber-300'
                  : 'bg-midnight-700 text-midnight-400'
              )}>
                {category.count}
              </span>
            </button>
          ))}
        </div>

        {/* Filters */}
        <div className="mt-6 space-y-2">
          <h3 className="text-sm font-semibold text-midnight-300 uppercase tracking-wider">
            Filters
          </h3>
          <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-midnight-400 hover:text-midnight-300 hover:bg-midnight-700/50 transition-colors">
            <Star className="w-4 h-4" />
            Featured Only
          </button>
          <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-midnight-400 hover:text-midnight-300 hover:bg-midnight-700/50 transition-colors">
            <Clock className="w-4 h-4" />
            Recently Updated
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="h-16 border-b border-midnight-700/50 px-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-midnight-100">Library</h1>
            <p className="text-sm text-midnight-400">
              {filteredItems.length} items found
            </p>
          </div>

          <div className="flex items-center gap-4">
            <button className="btn-cyber-outline">
              <Filter className="w-4 h-4 mr-2" />
              Filters
            </button>

            <div className="flex items-center border border-midnight-700 rounded-lg overflow-hidden">
              <button
                onClick={() => setViewMode('grid')}
                className={cn(
                  'px-3 py-2 flex items-center gap-2 text-sm transition-colors',
                  viewMode === 'grid'
                    ? 'bg-cyber-500/20 text-cyber-300'
                    : 'text-midnight-400 hover:text-midnight-300'
                )}
              >
                <Grid3X3 className="w-4 h-4" />
                Grid
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={cn(
                  'px-3 py-2 flex items-center gap-2 text-sm transition-colors',
                  viewMode === 'list'
                    ? 'bg-cyber-500/20 text-cyber-300'
                    : 'text-midnight-400 hover:text-midnight-300'
                )}
              >
                <List className="w-4 h-4" />
                List
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto scrollbar-cyber p-6">
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredItems.map((item) => (
                <div key={item.id} className="panel-midnight p-6 rounded-xl hover:border-cyber-500/50 transition-all duration-300 group">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-midnight-100 group-hover:text-cyber-300 transition-colors">
                          {item.name}
                        </h3>
                        {item.featured && (
                          <Star className="w-4 h-4 text-yellow-400 fill-current" />
                        )}
                      </div>
                      <p className="text-xs text-midnight-400">
                        by {item.author} • v{item.version}
                      </p>
                    </div>
                    <button className="btn-cyber-outline px-3 py-1 text-sm opacity-0 group-hover:opacity-100 transition-opacity">
                      <Download className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Description */}
                  <p className="text-sm text-midnight-300 mb-4 line-clamp-2">
                    {item.description}
                  </p>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-1 mb-4">
                    {item.tags.slice(0, 3).map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-midnight-700/50 text-xs text-midnight-400 rounded-md"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-between text-xs text-midnight-400">
                    <div className="flex items-center gap-2">
                      <div className="flex items-center gap-1">
                        <Star className="w-3 h-3 fill-current text-yellow-400" />
                        <span>{item.rating}</span>
                      </div>
                      <span>•</span>
                      <span>{item.downloads} downloads</span>
                    </div>
                    <span>{item.lastUpdated}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {filteredItems.map((item) => (
                <div key={item.id} className="panel-midnight p-4 rounded-lg hover:border-cyber-500/50 transition-all duration-300 group">
                  <div className="flex items-center gap-4">
                    {/* Icon */}
                    <div className="w-12 h-12 bg-gradient-cyber rounded-lg flex items-center justify-center flex-shrink-0">
                      <Tag className="w-6 h-6 text-midnight-900" />
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-midnight-100 group-hover:text-cyber-300 transition-colors">
                          {item.name}
                        </h3>
                        {item.featured && (
                          <Star className="w-4 h-4 text-yellow-400 fill-current" />
                        )}
                        <span className="text-xs text-midnight-400">v{item.version}</span>
                      </div>
                      <p className="text-sm text-midnight-300 mb-2 line-clamp-1">
                        {item.description}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-midnight-400">
                        <span>by {item.author}</span>
                        <div className="flex items-center gap-1">
                          <Star className="w-3 h-3 fill-current text-yellow-400" />
                          <span>{item.rating}</span>
                        </div>
                        <span>{item.downloads} downloads</span>
                        <span>{item.lastUpdated}</span>
                      </div>
                    </div>

                    {/* Actions */}
                    <button className="btn-cyber-outline px-4 py-2 text-sm opacity-0 group-hover:opacity-100 transition-opacity">
                      <Download className="w-4 h-4 mr-2" />
                      Install
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}