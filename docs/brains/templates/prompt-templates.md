# Master AI Brains - Prompt Templates

Comprehensive template guide for all AI session types in the TaylorDash system.

## Core Template Structure

### Universal Session Header
```
# [SESSION TYPE]: [SPECIFIC OBJECTIVE]

## Context
- **Project**: TaylorDash v1
- **Phase**: [Current development phase]
- **MCP Servers**: [Required MCP integrations]
- **Evidence Level**: [Basic/Detailed/Comprehensive]
- **Validation Required**: [Yes/No + specific criteria]

## Objective
[Single, measurable goal with success criteria]

## Constraints
- Token efficiency: Maximum 750 tokens per document
- Code quality: All changes must pass existing tests
- Documentation: Update relevant docs/brains/ files
- Performance: No degradation of core metrics
```

### Evidence Requirements by Level

**Basic Evidence**:
- Before/after code snippets
- Test execution results
- Basic functionality verification

**Detailed Evidence**:
- Performance metrics comparison
- Multi-scenario testing results
- Integration point validation
- Error handling verification

**Comprehensive Evidence**:
- Full system impact analysis
- Cross-component integration testing
- Performance profiling results
- Documentation validation
- User experience impact assessment

## Session Type Templates

### Development Session Template
```
# DEVELOPMENT SESSION: [Feature/Component Name]

## Context
- **Project**: TaylorDash v1
- **Phase**: [Development/Enhancement/Integration]
- **MCP Servers**: filesystem, database, api
- **Evidence Level**: Comprehensive
- **Validation Required**: Yes - functional testing + integration testing

## Objective
Build [specific feature] with [performance/quality requirements]

## Requirements
### Functional
- [Requirement 1 with acceptance criteria]
- [Requirement 2 with acceptance criteria]

### Technical
- Integration with existing [components]
- Performance target: [specific metrics]
- Error handling for [scenarios]

### Quality
- Test coverage: >90%
- Documentation: API docs + user guides
- Code review: Adherence to project standards

## Parallel Agent Coordination
1. **Primary Agent**: Core implementation
2. **Testing Agent**: Test suite development
3. **Documentation Agent**: Real-time documentation
4. **Integration Agent**: MCP server coordination

## Anti-Patterns to Avoid
- ❌ Building without tests
- ❌ Ignoring existing patterns
- ❌ Breaking backward compatibility
- ❌ Missing error handling
- ❌ Undocumented APIs

## Success Criteria
- [ ] Feature functions as specified
- [ ] All tests pass (existing + new)
- [ ] Documentation updated
- [ ] Performance targets met
- [ ] Integration points validated
```

### Debugging Session Template
```
# DEBUGGING SESSION: [Issue Description]

## Context
- **Project**: TaylorDash v1
- **Issue Type**: [Bug/Performance/Integration/Security]
- **Severity**: [Critical/High/Medium/Low]
- **MCP Servers**: filesystem, debugging, logging
- **Evidence Level**: Detailed
- **Validation Required**: Yes - reproduction + fix verification

## Problem Statement
[Clear, specific description of the issue]

## Investigation Plan
1. **Reproduce**: Create minimal reproduction case
2. **Isolate**: Identify affected components
3. **Analyze**: Root cause analysis
4. **Fix**: Implement targeted solution
5. **Validate**: Verify fix + prevent regression

## Diagnostic Checklist
- [ ] Error logs analyzed
- [ ] Network requests traced
- [ ] Database queries profiled
- [ ] Memory usage checked
- [ ] Performance metrics reviewed
- [ ] User flow tested

## Root Cause Analysis Framework
1. **Symptom**: What is observed?
2. **Immediate Cause**: Direct trigger?
3. **Root Cause**: Underlying system issue?
4. **Contributing Factors**: What made this possible?
5. **Prevention**: How to prevent similar issues?

## Anti-Patterns to Avoid
- ❌ Quick fixes without understanding
- ❌ Solving symptoms, not causes
- ❌ Introducing new risks
- ❌ Insufficient testing of fix
- ❌ Poor documentation of solution

## Success Criteria
- [ ] Issue reproduced and understood
- [ ] Root cause identified
- [ ] Fix implemented and tested
- [ ] Regression tests added
- [ ] Prevention measures documented
```

### Enhancement Session Template
```
# ENHANCEMENT SESSION: [Performance/UX/Feature Enhancement]

## Context
- **Project**: TaylorDash v1
- **Enhancement Type**: [Performance/UX/Feature/Integration]
- **Current Baseline**: [Measurable current state]
- **MCP Servers**: performance, analytics, filesystem
- **Evidence Level**: Comprehensive
- **Validation Required**: Yes - before/after comparison

## Objective
Improve [specific aspect] from [current state] to [target state]

## Baseline Metrics
- Performance: [current measurements]
- User Experience: [current pain points]
- System Health: [current status]

## Enhancement Plan
1. **Profile**: Measure current performance
2. **Identify**: Bottlenecks and opportunities
3. **Design**: Enhancement approach
4. **Implement**: Changes with monitoring
5. **Validate**: Improvement verification

## Success Metrics
- **Performance**: [specific targets]
- **Quality**: [quality improvements]
- **User Experience**: [UX improvements]

## Risk Assessment
- **Low Risk**: [changes with minimal impact]
- **Medium Risk**: [changes requiring careful testing]
- **High Risk**: [changes needing staged rollout]

## Anti-Patterns to Avoid
- ❌ Optimizing without measuring
- ❌ Breaking existing functionality
- ❌ Over-engineering solutions
- ❌ Ignoring edge cases
- ❌ Poor change communication

## Validation Requirements
- [ ] Baseline metrics captured
- [ ] Enhancement implemented
- [ ] Performance improvement verified
- [ ] No regression introduced
- [ ] User experience validated
```

### Validation Session Template
```
# VALIDATION SESSION: [System/Feature/Integration Validation]

## Context
- **Project**: TaylorDash v1
- **Validation Type**: [System/Integration/Performance/Security]
- **Scope**: [Specific components/features]
- **MCP Servers**: testing, monitoring, filesystem
- **Evidence Level**: Comprehensive
- **Validation Required**: Yes - systematic verification

## Validation Objectives
Primary: [Main validation goal]
Secondary: [Additional validation goals]

## Systematic Testing Approach
1. **Unit Level**: Component functionality
2. **Integration Level**: Component interaction
3. **System Level**: End-to-end workflows
4. **Performance Level**: Load and stress testing
5. **Security Level**: Vulnerability assessment

## Test Categories
### Functional Testing
- [ ] Core features work as expected
- [ ] Edge cases handled properly
- [ ] Error conditions managed

### Integration Testing
- [ ] API endpoints respond correctly
- [ ] Database operations succeed
- [ ] Third-party integrations work

### Performance Testing
- [ ] Response times within targets
- [ ] Resource usage acceptable
- [ ] Scalability requirements met

### Security Testing
- [ ] Authentication mechanisms secure
- [ ] Authorization properly enforced
- [ ] Data protection implemented

## Gap Analysis Framework
1. **Requirements vs Implementation**
2. **Expected vs Actual Behavior**
3. **Performance Targets vs Reality**
4. **Security Standards vs Current State**

## Priority Setting Criteria
- **P0**: Critical system functionality
- **P1**: Major feature completeness
- **P2**: Performance optimization
- **P3**: Nice-to-have improvements

## Anti-Patterns to Avoid
- ❌ Incomplete test coverage
- ❌ Ignoring edge cases
- ❌ Missing integration points
- ❌ Inadequate performance testing
- ❌ Poor documentation of results

## Success Criteria
- [ ] All critical paths validated
- [ ] Performance targets met
- [ ] Security requirements satisfied
- [ ] Integration points verified
- [ ] Gaps identified and prioritized
```

## MCP Integration Patterns

### Required MCP Servers by Session Type
- **Development**: filesystem, database, api, testing
- **Debugging**: filesystem, logging, debugging, monitoring
- **Enhancement**: performance, analytics, filesystem, monitoring
- **Validation**: testing, monitoring, filesystem, security

### MCP Usage Standards
```
## MCP Server Integration
- **Primary Server**: [main MCP server for this session]
- **Supporting Servers**: [additional required servers]
- **Data Flow**: [how data moves between servers]
- **Error Handling**: [MCP server failure scenarios]
```

## Agent Orchestration Standards

### Parallel Agent Patterns
1. **Lead Agent**: Session coordination and primary execution
2. **Specialist Agents**: Domain-specific tasks (testing, docs, performance)
3. **Validation Agent**: Quality assurance and verification
4. **Integration Agent**: MCP server coordination

### Communication Protocols
- Clear handoff points between agents
- Shared state management through MCP servers
- Consistent evidence documentation
- Coordinated validation processes

## Cross-Reference Links
- Core Brains: `/docs/brains/core/`
- Session History: `/docs/brains/sessions/`
- Project Standards: `/docs/brains/templates/project-specific/`
- MCP Integration: `/docs/brains/core/mcp-integration.md`

---
*Template Version: 1.0 | Last Updated: 2025-09-13*