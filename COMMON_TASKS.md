# Common Tasks Guide

## 🔗 How to Add a New API Endpoint

### 1. Define the Route (Backend)

**Location**: `backend/app/main.py` or `backend/app/routers/`

```python
# In main.py or create new router file
from fastapi import APIRouter, Depends, HTTPException
from .security import verify_api_key

@app.get("/api/v1/your-endpoint")
async def your_endpoint(api_key: str = Depends(verify_api_key)):
    """Your endpoint description"""
    try:
        # Your logic here
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Failed to process request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 2. Add Database Operations (if needed)

```python
async def your_endpoint(api_key: str = Depends(verify_api_key)):
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM your_table")
            data = [dict(row) for row in rows]
            return {"data": data}
    except Exception as e:
        # Handle error
```

### 3. Add Pydantic Schema (if needed)

**Location**: `backend/app/schemas.py`

```python
from pydantic import BaseModel, Field
from typing import Optional

class YourRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Item name")
    description: Optional[str] = Field(None, description="Item description")

class YourResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
```

### 4. Test the Endpoint

```bash
# Using curl
curl -H "X-API-Key: taylordash-dev-key" http://localhost:8000/api/v1/your-endpoint

# Check in Swagger UI
open http://localhost:8000/docs
```

## 🎨 How to Create a New React Component

### 1. Create Component File

**Location**: `frontend/src/components/YourComponent.tsx`

```tsx
import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import { notificationManager } from '../utils/errorHandling';

interface YourComponentProps {
  title?: string;
  onUpdate?: () => void;
}

export const YourComponent: React.FC<YourComponentProps> = ({
  title = "Default Title",
  onUpdate
}) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/api/v1/your-endpoint');
      setData(response.data);
      notificationManager.showSuccess('Data loaded successfully');
    } catch (error) {
      notificationManager.showError(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-4">{title}</h2>
      {loading ? (
        <p className="text-gray-400">Loading...</p>
      ) : (
        <div className="space-y-3">
          {data.map((item: any) => (
            <div key={item.id} className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-white font-medium">{item.name}</h3>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

### 2. Add to App Routing (if it's a page)

**Location**: `frontend/src/App.tsx`

```tsx
// Import your component
import { YourComponent } from './components/YourComponent';

// Add route in Routes section
<Route path="/your-page" element={
  <ProtectedRoute>
    <ErrorBoundary component="YourComponent">
      <Layout title="Your Page">
        <YourComponent />
      </Layout>
    </ErrorBoundary>
  </ProtectedRoute>
} />
```

### 3. Add Navigation Link

**Location**: `frontend/src/App.tsx` in Navigation component

```tsx
const navItems = [
  // ... existing items
  { path: '/your-page', icon: YourIcon, label: 'Your Page' },
];
```

## 🗄️ How to Add a New Database Table

### 1. Create Migration SQL

**Location**: `infra/postgres/init.sql` or create new migration file

```sql
-- Add to init.sql or create new migration
CREATE TABLE your_table (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_your_table_status ON your_table(status);
CREATE INDEX idx_your_table_created_at ON your_table(created_at);

-- Add foreign key constraints if needed
ALTER TABLE your_table ADD CONSTRAINT fk_your_table_project
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;
```

### 2. Update Database Schema

```bash
# If using Docker Compose
docker compose down
docker volume rm taylordashv1_postgres_data  # WARNING: This deletes data
docker compose up postgres -d

# Or run migration manually
psql postgresql://taylordash_app:password@localhost:5432/taylordash < your_migration.sql
```

### 3. Create Backend Model

**Location**: `backend/app/models/your_model.py`

```python
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class YourModel(Base):
    __tablename__ = "your_table"

    id = Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="active")
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
```

## 🔌 How to Create a Plugin

### 1. Create Plugin Directory

**Location**: `examples/your-plugin/`

```bash
mkdir -p examples/your-plugin/src
cd examples/your-plugin
```

### 2. Create Plugin Manifest

**Location**: `examples/your-plugin/plugin.json`

```json
{
  "name": "your-plugin",
  "version": "1.0.0",
  "title": "Your Plugin",
  "description": "Description of your plugin",
  "author": "Your Name",
  "entry_point": "src/App.tsx",
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "permissions": [
    "api:read",
    "api:write",
    "mqtt:subscribe",
    "mqtt:publish"
  ],
  "routes": [
    {
      "path": "/plugins/your-plugin",
      "component": "App"
    }
  ]
}
```

### 3. Create Plugin Component

**Location**: `examples/your-plugin/src/App.tsx`

```tsx
import React from 'react';

export const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="container mx-auto">
        <h1 className="text-3xl font-bold mb-6">Your Plugin</h1>
        <div className="bg-gray-800 rounded-lg p-6">
          <p className="text-gray-300">
            Your plugin content goes here.
          </p>
        </div>
      </div>
    </div>
  );
};

export default App;
```

### 4. Register Plugin in Frontend

**Location**: `frontend/src/plugins/registry.ts`

```tsx
export const pluginRegistry = {
  // ... existing plugins
  'your-plugin': {
    name: 'Your Plugin',
    path: '/plugins/your-plugin',
    component: () => import('../../examples/your-plugin/src/App'),
    icon: 'Puzzle',
    description: 'Description of your plugin'
  }
};
```

### 5. Add Backend Plugin Route (optional)

**Location**: `backend/app/routers/plugins.py`

```python
@router.get("/plugins/your-plugin/data")
async def get_your_plugin_data(api_key: str = Depends(verify_api_key)):
    """Get data for your plugin"""
    try:
        # Plugin-specific logic
        return {"status": "success", "data": plugin_data}
    except Exception as e:
        logger.error(f"Plugin error: {e}")
        raise HTTPException(status_code=500, detail="Plugin error")
```

## 🧪 How to Run Tests

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest tests/test_plugin_security.py

# Run with coverage
pytest --cov=app tests/

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_plugin_security.py::test_validate_plugin_manifest
```

### Frontend Tests

```bash
cd frontend

# Run unit tests (if configured)
npm test

# Type checking
npm run type-check

# Linting
npm run lint

# Build test
npm run build
```

### Integration Tests

```bash
# Full stack validation
bash ops/validate_p1.sh

# Manual API testing
curl -H "X-API-Key: taylordash-dev-key" http://localhost:8000/health/ready

# MQTT testing
mosquitto_pub -h localhost -t "test/topic" -m "hello" -u taylordash -P taylordash
mosquitto_sub -h localhost -t "tracker/events/#" -u taylordash -P taylordash
```

## 🐛 How to Debug Issues

### Backend Debugging

```bash
# View backend logs
docker compose logs -f backend

# Check database connection
docker compose exec postgres psql -U taylordash -d taylordash -c "SELECT 1;"

# Check MQTT connection
docker compose logs -f mosquitto

# API health check
curl -H "X-API-Key: taylordash-dev-key" http://localhost:8000/health/stack
```

### Frontend Debugging

```bash
# View frontend logs
docker compose logs -f frontend

# Check console in browser
# Open Developer Tools -> Console

# Check network requests
# Open Developer Tools -> Network

# Check local storage
console.log(localStorage.getItem('taylordash_session_token'));
```

### Database Debugging

```bash
# Connect to database
docker compose exec postgres psql -U taylordash -d taylordash

# Check tables
\dt

# Check specific data
SELECT * FROM projects LIMIT 5;
SELECT * FROM events_mirror ORDER BY created_at DESC LIMIT 10;

# Check connections
SELECT pid, usename, application_name, client_addr FROM pg_stat_activity;
```

### MQTT Debugging

```bash
# Test MQTT publishing
mosquitto_pub -h localhost -t "tracker/events/test" -m '{"test": true}' -u taylordash -P taylordash

# Monitor all MQTT messages
mosquitto_sub -h localhost -t "#" -u taylordash -P taylordash

# Check MQTT broker status
docker compose exec mosquitto mosquitto_passwd -U /mosquitto/config/password_file
```

## 🤖 For AI Agents

### Quick Context
These are the most common development tasks for extending TaylorDash. Follow the add-only principle - extend functionality through new endpoints, components, and plugins rather than modifying core files.

### Your Tools
- **Pattern**: Always use the existing patterns (API key auth, error handling, TypeScript types)
- **Command**: `bash ops/validate_p1.sh` (validate your changes)
- **File**: Check quick references for specific files to modify
- **Testing**: Use curl for API testing, browser dev tools for frontend

### Common Pitfalls
- ⚠️ Missing API key authentication on new endpoints
- ⚠️ Not handling errors properly (both backend and frontend)
- ⚠️ Forgetting to add database indexes for performance
- ⚠️ Not following TypeScript interfaces for new components
- ⚠️ Missing cleanup in React useEffect hooks

### Success Criteria
- ✅ New API endpoints return proper HTTP status codes
- ✅ Frontend components handle loading and error states
- ✅ Database operations use connection pooling correctly
- ✅ MQTT events are published for state changes
- ✅ All changes maintain the add-only architecture principle
- ✅ Tests pass and validation script succeeds