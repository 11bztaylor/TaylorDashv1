# TaylorDash-Specific Templates

Customized templates for TaylorDash development with dashboard-first principles, brand standards, and phase-specific optimizations.

## TaylorDash System Context

### Project Architecture
- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: Node.js + Express + JWT Authentication
- **Database**: PostgreSQL with connection pooling
- **Infrastructure**: Docker containerization
- **Monitoring**: Integrated logging and performance tracking

### Development Phases
- **Phase 1**: Core dashboard functionality ✓
- **Phase 2**: Advanced features and integrations (Current)
- **Phase 3**: Scalability and enterprise features
- **Phase 4**: AI/ML integration and automation

### Brand and Technical Standards
- **Performance**: Sub-300ms response times
- **Accessibility**: WCAG 2.1 AA compliance
- **Security**: JWT-based authentication, input sanitization
- **Code Quality**: 90%+ test coverage, TypeScript strict mode
- **UX**: Dashboard-first design, mobile-responsive

## TaylorDash Development Session Template

```
# TAYLORDASH DEVELOPMENT: [Feature Name]

## Context
- **Project**: TaylorDash v1
- **Phase**: [Phase 2/3/4] - [Specific phase objectives]
- **Component Type**: [Dashboard/Authentication/API/Integration]
- **MCP Servers**: filesystem, database, api, testing
- **Evidence Level**: Comprehensive
- **TaylorDash Standards**: Performance, Security, UX compliance required

## Dashboard-First Objective
Build [feature] that enhances dashboard experience with [specific user value]

**User Story**: As a [user type], I want [capability] so that [benefit]
**Dashboard Integration**: How this feature appears/integrates with main dashboard
**Performance Target**: [Specific TaylorDash performance requirements]

## TaylorDash-Specific Requirements
### Dashboard Integration Requirements
- [ ] **Main Dashboard View**: How feature appears on primary dashboard
- [ ] **Navigation Integration**: Menu/routing updates required
- [ ] **Real-time Updates**: Live data refresh requirements
- [ ] **Mobile Responsiveness**: Mobile dashboard experience

### Performance Requirements (TaylorDash Standards)
- [ ] **Initial Load**: <2 seconds for dashboard components
- [ ] **API Response**: <300ms for all API endpoints
- [ ] **Real-time Updates**: <100ms latency for live data
- [ ] **Memory Usage**: <50MB additional heap per feature

### Security Requirements (TaylorDash Standards)
- [ ] **JWT Integration**: Proper token validation
- [ ] **Role-Based Access**: Integration with existing user roles
- [ ] **Input Sanitization**: XSS and injection prevention
- [ ] **API Security**: Rate limiting and validation

### UX Requirements (TaylorDash Standards)
- [ ] **Consistent Design**: Follows established design system
- [ ] **Accessibility**: WCAG 2.1 AA compliance
- [ ] **Error Handling**: User-friendly error messages
- [ ] **Loading States**: Proper loading indicators

## TaylorDash Component Architecture
### Frontend Component Structure
```typescript
// TaylorDash component pattern
interface [FeatureName]Props {
  // Component props with TaylorDash standards
}

const [FeatureName]: React.FC<[FeatureName]Props> = ({}) => {
  // TaylorDash hooks and state management
  const { user } = useAuth(); // TaylorDash auth context
  const { dashboardData } = useDashboard(); // Dashboard context

  // Component implementation
  return (
    <DashboardLayout>
      {/* Feature implementation */}
    </DashboardLayout>
  );
};
```

### Backend API Pattern
```typescript
// TaylorDash API endpoint pattern
import { authenticateToken, validateInput } from '../middleware';

router.post('/api/[feature]',
  authenticateToken,
  validateInput([validation-schema]),
  async (req: Request, res: Response) => {
    try {
      // TaylorDash business logic
      const result = await [FeatureName]Service.execute(req.body);
      res.json({ success: true, data: result });
    } catch (error) {
      // TaylorDash error handling
      res.status(500).json({ success: false, error: error.message });
    }
  }
);
```

## TaylorDash Testing Strategy
### Component Testing (TaylorDash Standards)
```typescript
describe('[FeatureName] Component', () => {
  test('renders with dashboard context', async () => {
    render(
      <AuthProvider>
        <DashboardProvider>
          <[FeatureName] />
        </DashboardProvider>
      </AuthProvider>
    );
    // TaylorDash-specific assertions
  });

  test('meets performance requirements', async () => {
    const start = performance.now();
    render(<[FeatureName] />);
    const end = performance.now();
    expect(end - start).toBeLessThan(100); // TaylorDash standard
  });
});
```

### API Testing (TaylorDash Standards)
```typescript
describe('[Feature] API', () => {
  test('requires authentication', async () => {
    const response = await request(app)
      .post('/api/[feature]')
      .expect(401);
  });

  test('meets response time requirements', async () => {
    const start = Date.now();
    await request(app)
      .post('/api/[feature]')
      .set('Authorization', `Bearer ${validToken}`)
      .expect(200);
    const responseTime = Date.now() - start;
    expect(responseTime).toBeLessThan(300); // TaylorDash standard
  });
});
```

## TaylorDash-Specific Anti-Patterns
### Dashboard Design Anti-Patterns
❌ **Breaking Dashboard Consistency**
- Always use TaylorDash design system components
- Follow established color palette and typography

❌ **Ignoring Mobile Dashboard Experience**
- Test all dashboard features on mobile devices
- Ensure touch-friendly interactions

❌ **Poor Real-time Data Handling**
- Implement proper WebSocket or polling strategies
- Handle connection failures gracefully

### Performance Anti-Patterns
❌ **Exceeding TaylorDash Performance Budgets**
- Monitor bundle size increases
- Profile component render performance

❌ **Blocking Dashboard Loading**
- Use lazy loading for non-critical components
- Implement proper loading states

### Security Anti-Patterns
❌ **Bypassing TaylorDash Auth Patterns**
- Always use established auth middleware
- Never implement custom auth without review

## Success Criteria (TaylorDash Specific)
### Dashboard Integration Success
- [ ] Feature seamlessly integrates with main dashboard
- [ ] Consistent with TaylorDash design system
- [ ] Mobile dashboard experience optimized
- [ ] Real-time data updates working

### Performance Success (TaylorDash Targets)
- [ ] Initial load time <2 seconds
- [ ] API responses <300ms
- [ ] No memory leaks detected
- [ ] Bundle size increase <100KB

### User Experience Success
- [ ] WCAG 2.1 AA compliance verified
- [ ] User feedback positive (>4.0/5.0)
- [ ] Error handling tested and user-friendly
- [ ] Loading states implemented

---
```

## TaylorDash Debugging Session Template

```
# TAYLORDASH DEBUGGING: [Issue in Dashboard Context]

## Context
- **Project**: TaylorDash v1
- **Issue Type**: [Dashboard/Auth/API/Performance/Data]
- **User Impact**: [Dashboard functionality affected]
- **TaylorDash Component**: [Specific dashboard area affected]
- **Environment**: [Production/Staging with TaylorDash config]

## TaylorDash-Specific Issue Analysis
### Dashboard Impact Assessment
- [ ] **Main Dashboard Affected**: [Yes/No - describe impact]
- [ ] **User Workflows Broken**: [List affected user journeys]
- [ ] **Data Display Issues**: [Real-time data, charts, etc.]
- [ ] **Navigation Problems**: [Menu, routing issues]

### TaylorDash System Context
- [ ] **Authentication State**: [User session, JWT token status]
- [ ] **Database Connections**: [PostgreSQL pool status]
- [ ] **API Endpoints**: [Which TaylorDash APIs affected]
- [ ] **Frontend State**: [React context, component state]

## TaylorDash Debugging Checklist
### Frontend Debugging (React + TypeScript)
- [ ] **Browser Console**: Check for TypeScript/React errors
- [ ] **Network Tab**: Verify API calls and responses
- [ ] **React DevTools**: Component state and props inspection
- [ ] **Performance Tab**: Component render performance

### Backend Debugging (Node.js + Express)
- [ ] **Application Logs**: Check TaylorDash server logs
- [ ] **Database Logs**: PostgreSQL query performance/errors
- [ ] **JWT Token Validation**: Authentication middleware logs
- [ ] **API Response Times**: Performance monitoring data

### TaylorDash-Specific Logs
```bash
# TaylorDash log locations and patterns
docker-compose logs backend | grep "[ERROR]"
docker-compose logs frontend | grep "Failed to compile"
docker-compose logs postgres | grep "ERROR"

# Performance monitoring
curl -X GET http://localhost:3001/api/health
curl -X GET http://localhost:3001/api/metrics
```

## Common TaylorDash Issues and Solutions
### Dashboard Loading Issues
**Symptoms**: Blank dashboard, infinite loading
**Investigation**:
- Check API connectivity: `curl http://localhost:3001/api/dashboard`
- Verify JWT token in localStorage
- Check React error boundary logs

**Common Fixes**:
- Clear localStorage and re-authenticate
- Restart backend services
- Check database connection pool

### Authentication Issues
**Symptoms**: Redirect loops, 401 errors
**Investigation**:
- Check JWT token expiration
- Verify user role and permissions
- Check auth middleware configuration

**Common Fixes**:
- Refresh JWT tokens
- Clear authentication cache
- Restart auth service

### Real-time Data Issues
**Symptoms**: Stale dashboard data, missing updates
**Investigation**:
- Check WebSocket connections
- Verify polling intervals
- Test data refresh endpoints

**Common Fixes**:
- Restart WebSocket connections
- Clear data cache
- Check data synchronization logic

---
```

## TaylorDash Enhancement Session Template

```
# TAYLORDASH ENHANCEMENT: [Dashboard Improvement]

## Context
- **Project**: TaylorDash v1
- **Enhancement Type**: [Dashboard UX/Performance/Feature/Integration]
- **Current Dashboard State**: [Baseline metrics for affected area]
- **Target Improvement**: [Specific TaylorDash enhancement goals]
- **User Benefit**: [How this improves dashboard user experience]

## TaylorDash Enhancement Objectives
### Dashboard User Experience Goals
- **Reduce Task Completion Time**: From [current] to [target]
- **Improve Dashboard Load Time**: From [current] to [target]
- **Enhance Mobile Experience**: [Specific mobile improvements]
- **Increase User Satisfaction**: From [current score] to [target score]

### TaylorDash Performance Goals
- **API Response Time**: Maintain <300ms standard
- **Dashboard Render Time**: Improve to <2 seconds
- **Memory Usage**: Reduce by [X%] or maintain <50MB per feature
- **Bundle Size**: Minimize increase, target <100KB addition

## TaylorDash-Specific Enhancement Patterns
### Dashboard Performance Optimization
```typescript
// TaylorDash optimization patterns
import { memo, useMemo, useCallback } from 'react';
import { useDashboardOptimization } from '../hooks';

const OptimizedComponent = memo(({ data }: Props) => {
  const memoizedData = useMemo(() => processData(data), [data]);
  const optimizedCallback = useCallback((action) => {
    // TaylorDash performance-optimized callback
  }, [dependencies]);

  return <DashboardWidget data={memoizedData} onClick={optimizedCallback} />;
});
```

### Real-time Data Enhancement
```typescript
// TaylorDash real-time optimization
const useOptimizedRealTimeData = (endpoint: string) => {
  const [data, setData] = useState(null);

  useEffect(() => {
    // Optimized polling with exponential backoff
    const pollData = () => {
      fetch(`/api/${endpoint}`)
        .then(res => res.json())
        .then(setData);
    };

    const interval = setInterval(pollData, 5000);
    return () => clearInterval(interval);
  }, [endpoint]);

  return data;
};
```

## TaylorDash Enhancement Validation
### Dashboard UX Validation
- [ ] **User Task Testing**: Time key dashboard workflows
- [ ] **Mobile Responsiveness**: Test on target devices
- [ ] **Accessibility**: WCAG 2.1 AA compliance verification
- [ ] **Visual Consistency**: Design system compliance check

### Performance Validation (TaylorDash Standards)
```javascript
// TaylorDash performance testing
describe('TaylorDash Performance', () => {
  test('dashboard loads within 2 seconds', async () => {
    const start = performance.now();
    await render(<Dashboard />);
    const end = performance.now();
    expect(end - start).toBeLessThan(2000);
  });

  test('API responses under 300ms', async () => {
    const start = Date.now();
    const response = await fetch('/api/dashboard');
    const end = Date.now();
    expect(end - start).toBeLessThan(300);
  });
});
```

---
```

## TaylorDash Validation Session Template

```
# TAYLORDASH VALIDATION: [Dashboard System Validation]

## Context
- **Project**: TaylorDash v1
- **Validation Scope**: [Dashboard Area/Feature/Integration]
- **TaylorDash Standards**: All brand and technical standards apply
- **User Impact**: [Which dashboard users affected by validation]
- **Business Criticality**: [Impact on TaylorDash business objectives]

## TaylorDash-Specific Validation Criteria
### Dashboard Functionality Validation
- [ ] **Core Dashboard Features**: All primary dashboard functions working
- [ ] **User Authentication**: JWT-based auth system functioning
- [ ] **Real-time Data**: Live data updates working correctly
- [ ] **Mobile Dashboard**: Mobile experience fully functional
- [ ] **Cross-browser**: Chrome, Firefox, Safari, Edge compatibility

### TaylorDash Performance Standards Validation
- [ ] **Dashboard Load Time**: <2 seconds initial load
- [ ] **API Response Time**: <300ms for all endpoints
- [ ] **Real-time Updates**: <100ms latency for live data
- [ ] **Memory Usage**: <50MB per dashboard feature
- [ ] **Bundle Size**: Reasonable JavaScript bundle sizes

### TaylorDash Security Standards Validation
- [ ] **JWT Token Handling**: Proper token validation and refresh
- [ ] **Role-based Access**: User permissions enforced correctly
- [ ] **Input Sanitization**: XSS and injection prevention active
- [ ] **API Security**: Rate limiting and validation working
- [ ] **Data Protection**: Sensitive data properly encrypted

### TaylorDash UX Standards Validation
- [ ] **Design Consistency**: TaylorDash design system compliance
- [ ] **Accessibility**: WCAG 2.1 AA compliance verified
- [ ] **Error Handling**: User-friendly error messages displayed
- [ ] **Loading States**: Appropriate loading indicators shown
- [ ] **Responsive Design**: Optimal experience across device sizes

## TaylorDash Validation Test Suite
### Dashboard Integration Tests
```typescript
describe('TaylorDash Dashboard Integration', () => {
  test('complete user login to dashboard workflow', async () => {
    // Test full authentication and dashboard access flow
    await login('testuser@taylordash.com', 'password');
    await waitFor(() => screen.getByTestId('dashboard-main'));
    expect(screen.getByText('Welcome to TaylorDash')).toBeInTheDocument();
  });

  test('dashboard data loads and updates', async () => {
    render(<Dashboard />);
    await waitFor(() => screen.getByTestId('dashboard-data'));
    // Verify real-time data updates
    expect(screen.getByText(/Last updated:/)).toBeInTheDocument();
  });
});
```

### TaylorDash API Validation
```typescript
describe('TaylorDash API Validation', () => {
  test('all dashboard endpoints respond correctly', async () => {
    const endpoints = ['/api/dashboard', '/api/users', '/api/projects'];
    for (const endpoint of endpoints) {
      const response = await request(app)
        .get(endpoint)
        .set('Authorization', `Bearer ${validToken}`)
        .expect(200);
      expect(response.body.success).toBe(true);
    }
  });
});
```

## TaylorDash Gap Analysis Framework
### Dashboard Experience Gaps
- **Usability Gaps**: [Areas where dashboard UX can improve]
- **Performance Gaps**: [Performance issues affecting user experience]
- **Feature Gaps**: [Missing dashboard functionality]
- **Accessibility Gaps**: [Areas not meeting WCAG standards]

### Technical Architecture Gaps
- **Scalability Gaps**: [Areas that won't scale with user growth]
- **Security Gaps**: [Security improvements needed]
- **Code Quality Gaps**: [Technical debt and maintainability issues]
- **Documentation Gaps**: [Missing or outdated documentation]

### TaylorDash Business Gaps
- **User Adoption Gaps**: [Features with low adoption rates]
- **Competitive Gaps**: [Areas where competitors have advantages]
- **Market Fit Gaps**: [Features not meeting market needs]
- **ROI Gaps**: [Features not providing expected business value]

---
```

## TaylorDash MCP Integration Patterns

### Dashboard-Specific MCP Usage
```javascript
// TaylorDash MCP server integration patterns
const dashboardMCP = {
  filesystem: {
    // Dashboard component and asset management
    usage: ['component-files', 'static-assets', 'configuration'],
    patterns: ['lazy-loading', 'asset-optimization', 'hot-reload']
  },

  database: {
    // Dashboard data and user management
    usage: ['user-data', 'dashboard-config', 'real-time-data'],
    patterns: ['connection-pooling', 'query-optimization', 'data-caching']
  },

  api: {
    // Dashboard API coordination
    usage: ['endpoint-testing', 'response-validation', 'performance-monitoring'],
    patterns: ['jwt-integration', 'rate-limiting', 'error-handling']
  },

  monitoring: {
    // Dashboard performance and health
    usage: ['performance-metrics', 'user-analytics', 'error-tracking'],
    patterns: ['real-time-dashboards', 'alerting', 'trend-analysis']
  }
};
```

## Phase-Specific Customizations

### Phase 2: Advanced Features (Current)
- **Focus**: Enhanced dashboard functionality and integrations
- **Standards**: Maintain performance while adding features
- **Testing**: Comprehensive integration testing required
- **Documentation**: API documentation and user guides mandatory

### Phase 3: Scalability and Enterprise
- **Focus**: Performance optimization and enterprise features
- **Standards**: Sub-200ms API responses, enterprise security
- **Testing**: Load testing and security audits required
- **Documentation**: Architecture documentation and scaling guides

### Phase 4: AI/ML Integration
- **Focus**: Intelligent dashboard features and automation
- **Standards**: ML model performance integration
- **Testing**: AI model validation and bias testing
- **Documentation**: AI feature documentation and ethical guidelines

## Cross-Reference Links (TaylorDash Specific)
- **TaylorDash Architecture**: `/docs/architecture/`
- **Component Library**: `/frontend/src/components/`
- **API Documentation**: `/docs/api/`
- **Design System**: `/docs/design-system/`
- **Performance Standards**: `/docs/performance/`
- **Security Guidelines**: `/docs/security/`

---
*TaylorDash Templates v1.0 | Customized for TaylorDash Master AI Brains System*