# Architecture Principles for TaylorDash Systems
*Universal design patterns and standards for all TaylorDash projects*

## Core Architectural Philosophy

### The Add-Only Principle
**Definition**: Systems evolve by adding new components, never by modifying existing core functionality.

**Implementation Guidelines**:
- Extend functionality through adapters, plugins, and event consumers
- Core components are immutable after initial development
- New features bolt on via well-defined interfaces
- Backward compatibility is never broken

**Benefits**:
- Zero risk of breaking existing functionality
- Clear upgrade paths without migration complexity
- Parallel development without conflicts
- Easy rollback of problematic features

**Example Pattern**:
```typescript
// DON'T: Modify core component
class ProjectManager {
  createProject() { /* existing logic */ }
  // ❌ Adding feature directly
  createProjectWithTemplate() { /* new feature */ }
}

// DO: Extend through adapter
interface ProjectCreationAdapter {
  enhance(request: CreateProjectRequest): CreateProjectRequest;
}

class TemplateAdapter implements ProjectCreationAdapter {
  enhance(request) { /* template logic */ }
}
```

### Event-Driven Architecture
**Definition**: Components communicate through events on a message bus, not direct API calls.

**Core Patterns**:
- **Publisher/Subscriber**: Loose coupling through MQTT topics
- **Event Sourcing**: All state changes captured as events
- **CQRS**: Separate command and query responsibilities
- **Saga Pattern**: Distributed transactions through event orchestration

**Event Contract Standards**:
```json
{
  "trace_id": "uuid-v4",           // Required for distributed tracing
  "event_type": "domain.action",   // Required: namespace.verb format
  "timestamp": "ISO-8601",         // Required: UTC timezone
  "source": "service-name",        // Required: publishing service
  "version": "semver",             // Required: schema version
  "correlation_id": "uuid-v4",     // Optional: related events
  "data": {},                      // Required: event payload
  "metadata": {}                   // Optional: additional context
}
```

**Topic Naming Convention**:
```
{system}/{domain}/{action}
taylor/projects/created
taylor/plugins/installed
taylor/users/authenticated
```

### Security-First Design
**Definition**: Security considerations are built into every architectural decision from the beginning.

**Core Security Patterns**:

#### 1. Zero Trust Architecture
```
- Never trust, always verify
- Explicit permission grants
- Least privilege principle
- Continuous security validation
```

#### 2. Plugin Sandboxing Model
```typescript
interface PluginSandbox {
  // Isolated execution environment
  execute(plugin: Plugin, context: SandboxContext): Promise<Result>;

  // Capability-based permissions
  grantCapability(plugin: Plugin, capability: SecurityCapability): void;

  // Communication proxy
  proxyApiCall(request: PluginApiRequest): Promise<FilteredResponse>;
}
```

#### 3. API Security Layers
```
1. Edge Layer: Traefik TLS termination + security headers
2. Auth Layer: OIDC token validation + RBAC
3. API Layer: Request validation + rate limiting
4. Data Layer: Column-level encryption + audit trails
```

#### 4. Secrets Management
```bash
# Environment-based secrets (development)
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# Docker secrets (production)
docker secret create postgres_password /path/to/secret
```

### Observability-First Architecture
**Definition**: Every component is instrumented for monitoring, tracing, and debugging from day one.

**Three Pillars Implementation**:

#### 1. Distributed Tracing
```typescript
// OpenTelemetry tracing pattern
import { trace, context } from '@opentelemetry/api';

async function processProject(projectId: string) {
  const span = trace.getActiveSpan() || trace.startSpan('process-project');

  try {
    span.setAttributes({
      'project.id': projectId,
      'service.name': 'project-service'
    });

    // Business logic with child spans
    await database.save(project);
    await eventBus.publish(event);

    span.setStatus({ code: SpanStatusCode.OK });
  } catch (error) {
    span.recordException(error);
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: error.message
    });
    throw error;
  } finally {
    span.end();
  }
}
```

#### 2. Structured Metrics
```typescript
// Prometheus metrics patterns
import { Counter, Histogram, Gauge } from 'prom-client';

const projectsTotal = new Counter({
  name: 'taylor_projects_total',
  help: 'Total number of projects created',
  labelNames: ['status', 'template', 'user_role']
});

const apiDuration = new Histogram({
  name: 'taylor_api_request_duration_seconds',
  help: 'API request duration in seconds',
  labelNames: ['method', 'endpoint', 'status_code'],
  buckets: [0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10]
});
```

#### 3. Centralized Logging
```typescript
// Structured logging pattern
import { Logger } from 'winston';

const logger = Logger.createLogger({
  format: combine(
    timestamp(),
    errors({ stack: true }),
    json()
  )
});

// Usage with trace correlation
logger.info('Project created', {
  project_id: projectId,
  user_id: userId,
  trace_id: context.traceId,
  span_id: context.spanId,
  event_type: 'project.created'
});
```

## Storage Architecture Patterns

### Multi-Model Storage Strategy
**Definition**: Use the right storage engine for each data type and access pattern.

#### 1. OLTP Database (PostgreSQL)
**Use Cases**:
- Transactional data requiring ACID compliance
- Normalized data with complex relationships
- User management and configuration

**Schema Design Principles**:
```sql
-- Event sourcing table
CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  aggregate_id UUID NOT NULL,
  event_type VARCHAR(100) NOT NULL,
  event_data JSONB NOT NULL,
  trace_id UUID NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  version INTEGER NOT NULL
);

-- Optimized indexes
CREATE INDEX idx_events_aggregate ON events (aggregate_id, version);
CREATE INDEX idx_events_type ON events (event_type, created_at);
CREATE INDEX idx_events_trace ON events (trace_id);
```

#### 2. Time-Series Database (VictoriaMetrics)
**Use Cases**:
- Metrics and performance data
- High-volume event streams
- Analytics and monitoring

**Data Model**:
```
# Metric naming convention
{system}_{component}_{measurement}_{unit}
taylor_api_requests_total
taylor_database_connections_active
taylor_plugin_execution_duration_seconds

# Label strategy (high cardinality)
taylor_api_requests_total{method="GET", endpoint="/projects", status="200"}
```

#### 3. Object Storage (MinIO)
**Use Cases**:
- File uploads and artifacts
- Backup and archival data
- Plugin assets and resources

**Bucket Strategy**:
```
Projects:
  taylor-projects/{project-id}/artifacts/
  taylor-projects/{project-id}/exports/

Plugins:
  taylor-plugins/{plugin-id}/assets/
  taylor-plugins/{plugin-id}/versions/

System:
  taylor-backups/{date}/
  taylor-logs/{service}/{date}/
```

### Data Consistency Patterns

#### 1. Event Sourcing with CQRS
```typescript
// Command side (write model)
class ProjectCommandHandler {
  async handle(command: CreateProjectCommand): Promise<void> {
    const events = await this.aggregate.process(command);
    await this.eventStore.save(events);
    await this.eventBus.publish(events);
  }
}

// Query side (read model)
class ProjectQueryHandler {
  async handle(query: GetProjectQuery): Promise<ProjectView> {
    return await this.readModel.findById(query.projectId);
  }

  // Event handler to update read model
  async on(event: ProjectCreatedEvent): Promise<void> {
    const view = this.createProjectView(event);
    await this.readModel.save(view);
  }
}
```

#### 2. Saga Pattern for Distributed Transactions
```typescript
class ProjectCreationSaga {
  async handle(event: ProjectCreationRequested) {
    try {
      // Step 1: Reserve resources
      await this.sendCommand(new ReserveResourcesCommand(event.projectId));

      // Step 2: Create project
      await this.sendCommand(new CreateProjectCommand(event.projectId));

      // Step 3: Initialize plugins
      await this.sendCommand(new InitializePluginsCommand(event.projectId));

      // Success: Complete saga
      await this.publish(new ProjectCreationCompleted(event.projectId));

    } catch (error) {
      // Compensation: Rollback changes
      await this.sendCommand(new ReleaseResourcesCommand(event.projectId));
      await this.publish(new ProjectCreationFailed(event.projectId, error));
    }
  }
}
```

## Performance Architecture Standards

### Async-First Design
**Definition**: All I/O operations use non-blocking async patterns to maximize throughput.

#### Backend Async Patterns (Python FastAPI)
```python
from typing import AsyncGenerator
import asyncpg
import aioredis

class DatabaseService:
    async def __aenter__(self):
        self.pool = await asyncpg.create_pool(DATABASE_URL)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.pool.close()

    async def get_projects(self, user_id: str) -> List[Project]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM projects WHERE user_id = $1", user_id
            )
            return [Project.from_row(row) for row in rows]

# Dependency injection with async context managers
async def get_database() -> AsyncGenerator[DatabaseService, None]:
    async with DatabaseService() as db:
        yield db
```

#### Frontend Async Patterns (React)
```typescript
// Concurrent API calls with proper error handling
const useProjectsData = (userId: string) => {
  const [state, setState] = useState<ProjectsState>({
    projects: [],
    metrics: null,
    loading: true,
    error: null
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setState(prev => ({ ...prev, loading: true, error: null }));

        // Concurrent requests
        const [projectsResponse, metricsResponse] = await Promise.allSettled([
          api.getProjects(userId),
          api.getProjectMetrics(userId)
        ]);

        // Handle partial failures gracefully
        const projects = projectsResponse.status === 'fulfilled'
          ? projectsResponse.value : [];
        const metrics = metricsResponse.status === 'fulfilled'
          ? metricsResponse.value : null;

        setState({
          projects,
          metrics,
          loading: false,
          error: projectsResponse.status === 'rejected'
            ? projectsResponse.reason : null
        });
      } catch (error) {
        setState(prev => ({ ...prev, loading: false, error }));
      }
    };

    fetchData();
  }, [userId]);

  return state;
};
```

### Caching Strategy Architecture

#### Multi-Level Caching
```
1. Browser Cache: Static assets with versioned URLs (1 year)
2. CDN Cache: API responses with ETags (1 hour)
3. Application Cache: Database query results (5 minutes)
4. Database Cache: Query plans and buffer pools
```

#### Cache Invalidation Patterns
```typescript
// Event-driven cache invalidation
class CacheInvalidationService {
  async onProjectUpdated(event: ProjectUpdatedEvent) {
    const keys = [
      `projects:user:${event.userId}`,
      `project:${event.projectId}`,
      `metrics:project:${event.projectId}`
    ];

    await Promise.all(keys.map(key => this.cache.delete(key)));

    // Proactive refresh for hot data
    if (event.isHotProject) {
      await this.preloadProjectData(event.projectId);
    }
  }
}
```

## Component Architecture Standards

### React Component Patterns

#### 1. Compound Component Pattern
```typescript
// Flexible, composable components
const ProjectCard = {
  Root: ({ children, project }) => (
    <div className="project-card" data-testid={`project-${project.id}`}>
      <ProjectContext.Provider value={project}>
        {children}
      </ProjectContext.Provider>
    </div>
  ),

  Header: ({ children }) => (
    <div className="project-card-header">
      {children}
    </div>
  ),

  Title: () => {
    const project = useContext(ProjectContext);
    return <h3>{project.name}</h3>;
  },

  Status: () => {
    const project = useContext(ProjectContext);
    return <Badge status={project.status} />;
  },

  Actions: ({ children }) => (
    <div className="project-card-actions">
      {children}
    </div>
  )
};

// Usage
<ProjectCard.Root project={project}>
  <ProjectCard.Header>
    <ProjectCard.Title />
    <ProjectCard.Status />
  </ProjectCard.Header>
  <ProjectCard.Actions>
    <Button>Edit</Button>
    <Button>Delete</Button>
  </ProjectCard.Actions>
</ProjectCard.Root>
```

#### 2. Custom Hooks Pattern
```typescript
// Reusable business logic
const useProjectManagement = () => {
  const { user } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);

  const createProject = useCallback(async (data: CreateProjectData) => {
    setLoading(true);
    try {
      const project = await api.createProject(data);
      setProjects(prev => [...prev, project]);

      // Emit event for other components
      eventBus.emit('project:created', { project, user: user.id });

      return project;
    } finally {
      setLoading(false);
    }
  }, [user]);

  const deleteProject = useCallback(async (projectId: string) => {
    await api.deleteProject(projectId);
    setProjects(prev => prev.filter(p => p.id !== projectId));

    eventBus.emit('project:deleted', { projectId, user: user.id });
  }, [user]);

  return {
    projects,
    loading,
    createProject,
    deleteProject,
    refetch: () => fetchProjects()
  };
};
```

### Error Handling Architecture

#### 1. Error Boundary Pattern
```typescript
class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log to observability system
    logger.error('React component error', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      trace_id: getCurrentTraceId()
    });

    // Report to error tracking
    errorReporting.captureException(error, {
      tags: { component: 'error-boundary' },
      extra: errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <ErrorFallback
          error={this.state.error}
          onRetry={() => this.setState({ hasError: false, error: null })}
        />
      );
    }

    return this.props.children;
  }
}
```

#### 2. API Error Handling
```typescript
// Centralized API error handling
class ApiClient {
  async request<T>(config: RequestConfig): Promise<T> {
    try {
      const response = await axios(config);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const apiError = this.transformError(error);

        // Emit error event for global handling
        eventBus.emit('api:error', apiError);

        throw apiError;
      }
      throw error;
    }
  }

  private transformError(error: AxiosError): ApiError {
    const status = error.response?.status;
    const data = error.response?.data as any;

    switch (status) {
      case 401:
        // Trigger auth refresh
        authService.refreshToken();
        return new AuthenticationError(data.message);

      case 403:
        return new AuthorizationError(data.message);

      case 422:
        return new ValidationError(data.detail);

      default:
        return new ApiError(data.message || 'Unknown error');
    }
  }
}
```

## Testing Architecture Standards

### Test Pyramid Strategy
```
E2E Tests (10%):    Full user workflows with Playwright
Integration (20%):  API + Database + MQTT integration
Unit Tests (70%):   Components, services, utilities
```

### Testing Patterns

#### 1. Component Testing with Testing Library
```typescript
// Component tests focus on behavior, not implementation
describe('ProjectCard', () => {
  it('allows user to edit project when authorized', async () => {
    const mockProject = createMockProject();
    const mockUser = createMockUser({ role: 'maintainer' });

    render(
      <AuthContext.Provider value={{ user: mockUser }}>
        <ProjectCard project={mockProject} />
      </AuthContext.Provider>
    );

    // User interaction
    const editButton = screen.getByRole('button', { name: /edit/i });
    await user.click(editButton);

    // Verify behavior
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByDisplayValue(mockProject.name)).toBeInTheDocument();
  });
});
```

#### 2. Integration Testing
```python
# API integration tests
@pytest.mark.asyncio
async def test_create_project_integration(client, db_session, mqtt_client):
    # Setup
    user = await create_test_user(db_session)
    project_data = {
        "name": "Test Project",
        "description": "Integration test project"
    }

    # Execute
    response = await client.post(
        "/api/projects",
        json=project_data,
        headers={"Authorization": f"Bearer {user.token}"}
    )

    # Verify API response
    assert response.status_code == 201
    project = response.json()
    assert project["name"] == project_data["name"]

    # Verify database persistence
    db_project = await db_session.get(Project, project["id"])
    assert db_project is not None
    assert db_project.name == project_data["name"]

    # Verify MQTT event published
    event = await mqtt_client.wait_for_message("taylor/projects/created")
    assert event["data"]["project_id"] == project["id"]
```

## Deployment Architecture Standards

### Container Architecture
```dockerfile
# Multi-stage build pattern for minimal production images
FROM node:18-alpine AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force
COPY . .
RUN npm run build

FROM nginx:alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose Architecture
```yaml
# Production-ready compose with health checks
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      target: production-stage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - MQTT_URL=${MQTT_URL}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    depends_on:
      postgres:
        condition: service_healthy
      mqtt:
        condition: service_healthy
    restart: unless-stopped

networks:
  taylor-net:
    driver: bridge
```

These architectural principles provide the foundation for consistent, scalable, and maintainable TaylorDash systems across all projects and phases.