# Development Session Template

Template for building new features with parallel agent orchestration and comprehensive validation.

## Copy-Paste Template

```
# DEVELOPMENT SESSION: [Feature/Component Name]

## Context
- **Project**: TaylorDash v1
- **Phase**: [Development/Enhancement/Integration]
- **MCP Servers**: filesystem, database, api, testing
- **Evidence Level**: Comprehensive
- **Validation Required**: Yes - functional testing + integration testing
- **Lead Agent**: [Primary implementation agent]
- **Supporting Agents**: [Testing, Documentation, Integration agents]

## Objective
Build [specific feature] with [performance/quality requirements]

Success Criteria: [Measurable outcomes]

## Requirements Analysis
### Functional Requirements
- [ ] [Requirement 1] - Acceptance: [criteria]
- [ ] [Requirement 2] - Acceptance: [criteria]
- [ ] [Requirement 3] - Acceptance: [criteria]

### Technical Requirements
- [ ] Integration with [existing components]
- [ ] Performance target: [specific metrics]
- [ ] Error handling for [specific scenarios]
- [ ] API compatibility: [version/standards]

### Quality Requirements
- [ ] Test coverage: >90%
- [ ] Documentation: API docs + user guides
- [ ] Code review: Project standards compliance
- [ ] Performance: No degradation of core metrics

## Parallel Agent Coordination Plan
### Agent Assignments
1. **Primary Agent** (Lead)
   - Core feature implementation
   - Architecture decisions
   - Integration coordination

2. **Testing Agent**
   - Test suite development
   - Coverage verification
   - Performance testing

3. **Documentation Agent**
   - API documentation
   - User guide updates
   - Code commenting

4. **Integration Agent**
   - MCP server coordination
   - Database schema updates
   - External service integration

### Handoff Points
- [ ] Requirements → Design (All agents review)
- [ ] Design → Implementation (Primary leads)
- [ ] Implementation → Testing (Testing agent validates)
- [ ] Testing → Documentation (Documentation agent updates)
- [ ] Documentation → Integration (Integration agent verifies)

## Implementation Plan
### Phase 1: Foundation
- [ ] Database schema changes
- [ ] Core component structure
- [ ] Basic API endpoints
- [ ] Initial test framework

### Phase 2: Core Logic
- [ ] Business logic implementation
- [ ] Data processing functions
- [ ] Error handling
- [ ] Validation logic

### Phase 3: Integration
- [ ] Frontend component integration
- [ ] API endpoint completion
- [ ] Database operation testing
- [ ] MCP server integration

### Phase 4: Validation
- [ ] Comprehensive testing
- [ ] Performance validation
- [ ] Documentation review
- [ ] Integration verification

## MCP Server Integration Requirements
### Primary MCP Servers
- **filesystem**: Code management and file operations
- **database**: Schema updates and data operations
- **api**: Endpoint testing and validation
- **testing**: Test execution and coverage reporting

### Integration Patterns
```javascript
// MCP Server Usage Example
const mcpFilesystem = await getMCPServer('filesystem');
const mcpDatabase = await getMCPServer('database');

// Coordinated operations
await mcpDatabase.updateSchema(schemaChanges);
await mcpFilesystem.writeFiles(implementationFiles);
```

### Error Handling
- MCP server unavailable: [fallback strategy]
- Data synchronization issues: [resolution approach]
- Integration failures: [rollback procedures]

## Anti-Patterns Prevention
### Code Quality Anti-Patterns
❌ **Building without tests**
- Every function must have corresponding tests
- Test-driven development preferred

❌ **Ignoring existing patterns**
- Review `/frontend/src/` for established patterns
- Follow TypeScript/React conventions in codebase

❌ **Breaking backward compatibility**
- API versioning for breaking changes
- Migration scripts for database changes

❌ **Missing error handling**
- All async operations must handle errors
- User-friendly error messages required

❌ **Undocumented APIs**
- OpenAPI spec updates mandatory
- Code comments for complex logic

### Architecture Anti-Patterns
❌ **Tight coupling**
- Use dependency injection
- Interface-based design

❌ **God objects**
- Single responsibility principle
- Component decomposition

❌ **Hardcoded configurations**
- Environment-based configuration
- Feature flags for rollouts

## Testing Strategy
### Unit Testing
- Individual function testing
- Mock external dependencies
- Edge case coverage

### Integration Testing
- API endpoint testing
- Database operation testing
- Component interaction testing

### End-to-End Testing
- User workflow validation
- Cross-browser testing
- Performance under load

### Test Coverage Requirements
- Minimum 90% line coverage
- 100% critical path coverage
- Error scenario testing

## Evidence Collection Requirements
### Before Implementation
- [ ] Baseline performance metrics
- [ ] Current system state documentation
- [ ] Requirements validation

### During Implementation
- [ ] Code review artifacts
- [ ] Test execution results
- [ ] Performance monitoring data

### After Implementation
- [ ] Feature demonstration
- [ ] Performance comparison
- [ ] Integration verification
- [ ] Documentation completeness

## Documentation Requirements
### API Documentation
- OpenAPI specification updates
- Request/response examples
- Error code documentation

### User Documentation
- Feature usage guide
- Configuration instructions
- Troubleshooting section

### Developer Documentation
- Architecture decisions
- Integration patterns
- Maintenance procedures

## Success Validation Checklist
### Functional Validation
- [ ] All requirements implemented
- [ ] Edge cases handled
- [ ] Error scenarios tested
- [ ] User workflows verified

### Technical Validation
- [ ] Performance targets met
- [ ] Integration points working
- [ ] Security requirements satisfied
- [ ] Scalability considerations addressed

### Quality Validation
- [ ] Code review completed
- [ ] Test coverage achieved
- [ ] Documentation updated
- [ ] Standards compliance verified

### Integration Validation
- [ ] MCP servers coordinated
- [ ] Database changes applied
- [ ] API endpoints tested
- [ ] Frontend integration verified

## Rollback Plan
### Immediate Rollback Triggers
- Critical functionality broken
- Performance degradation >20%
- Security vulnerabilities introduced
- Data corruption detected

### Rollback Procedure
1. [ ] Stop new feature deployment
2. [ ] Revert database migrations
3. [ ] Restore previous code version
4. [ ] Verify system stability
5. [ ] Document rollback reason

## Post-Implementation Actions
### Monitoring Setup
- [ ] Performance metrics monitoring
- [ ] Error tracking configuration
- [ ] User adoption tracking
- [ ] System health monitoring

### Knowledge Transfer
- [ ] Team walkthrough session
- [ ] Documentation review
- [ ] Best practices documentation
- [ ] Lessons learned capture

## Template Usage Notes
1. **Customization**: Adapt sections based on feature complexity
2. **Agent Coordination**: Assign specific agents to defined roles
3. **MCP Integration**: Ensure all required servers are available
4. **Evidence Collection**: Document everything for future reference
5. **Quality Gates**: Don't skip validation checkpoints

---
*Development Session Template v1.0 | TaylorDash Master AI Brains System*
```