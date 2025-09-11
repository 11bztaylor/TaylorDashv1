# TaylorDash Frontend

A modern React application with TypeScript, Vite, and Tailwind CSS providing a visual shell interface.

## Features

- **React 18+** with TypeScript for type-safe development
- **Vite** for fast development and optimized builds
- **Tailwind CSS** with custom midnight/cyber theme
- **React Router DOM** for client-side routing
- **React Flow** for canvas functionality
- **Responsive design** with mobile-first approach
- **Custom components** following TaylorDash design system

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/         # Reusable UI components
│   ├── AppShell.tsx   # Main application layout
│   ├── Navigation.tsx # Sidebar navigation
│   └── StatusBar.tsx  # Bottom status bar
├── pages/             # Page components
│   ├── HomePage.tsx   # Landing/dashboard page
│   ├── CanvasPage.tsx # Canvas workspace
│   ├── LibraryPage.tsx# Widget/template library
│   ├── PluginsPage.tsx# Plugin management
│   └── SettingsPage.tsx# Application settings
├── hooks/             # Custom React hooks
├── types/             # TypeScript type definitions
├── utils/             # Utility functions
├── styles/            # Global styles and CSS
└── main.tsx          # Application entry point
```

## Theme System

The application uses a custom theme system based on:

- **Midnight palette**: Dark base colors (midnight-50 to midnight-950)
- **Cyber accents**: Green to orange gradient (#00ff41 to #ff6b35)
- **Typography**: Inter for UI, JetBrains Mono for code
- **Components**: Custom Tailwind utility classes

## Development

### Adding New Pages

1. Create component in `src/pages/`
2. Add route to `src/App.tsx`
3. Update navigation in `src/components/Navigation.tsx`

### Adding New Components

1. Create component in `src/components/`
2. Export from appropriate index file
3. Follow existing naming conventions

### Styling Guidelines

- Use Tailwind utility classes
- Leverage custom theme tokens (midnight-*, cyber-*, neon-*)
- Use custom component classes (.btn-cyber, .panel-midnight, etc.)
- Follow responsive-first approach

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler check

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new features
3. Test responsive design on multiple screen sizes
4. Ensure accessibility best practices