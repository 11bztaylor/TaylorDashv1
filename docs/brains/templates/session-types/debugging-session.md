# Debugging Session Template

Template for investigation and fixes with systematic diagnostic approach and prevention documentation.

## Copy-Paste Template

```
# DEBUGGING SESSION: [Issue Description]

## Context
- **Project**: TaylorDash v1
- **Issue Type**: [Bug/Performance/Integration/Security/UX]
- **Severity**: [Critical/High/Medium/Low]
- **MCP Servers**: filesystem, logging, debugging, monitoring
- **Evidence Level**: Detailed
- **Validation Required**: Yes - reproduction + fix verification
- **Reporter**: [User/System/Monitor]
- **Environment**: [Production/Staging/Development]

## Problem Statement
**Issue**: [Clear, specific description of the problem]
**Impact**: [Who/what is affected and how]
**Frequency**: [How often does this occur]
**Business Impact**: [Cost/user experience impact]

## Initial Assessment
### Symptoms Observed
- [ ] [Symptom 1]: [Description and frequency]
- [ ] [Symptom 2]: [Description and frequency]
- [ ] [Symptom 3]: [Description and frequency]

### Affected Components
- [ ] Frontend: [Specific components/pages]
- [ ] Backend: [APIs/services affected]
- [ ] Database: [Tables/queries involved]
- [ ] Infrastructure: [Servers/services impacted]

### User Impact
- [ ] Critical workflows broken: [List workflows]
- [ ] Performance degradation: [Specific metrics]
- [ ] Data integrity issues: [Types of data affected]
- [ ] Security implications: [Potential vulnerabilities]

## Investigation Plan
### Phase 1: Reproduction (Lead Agent)
- [ ] Create minimal reproduction case
- [ ] Document exact steps to reproduce
- [ ] Identify conditions that trigger issue
- [ ] Capture error messages/logs

### Phase 2: Isolation (Analysis Agent)
- [ ] Identify affected system boundaries
- [ ] Rule out unrelated components
- [ ] Trace data flow through system
- [ ] Isolate root cause component

### Phase 3: Analysis (Investigation Agent)
- [ ] Deep dive into root cause component
- [ ] Analyze code logic and data flow
- [ ] Review recent changes and deployments
- [ ] Examine system interactions

### Phase 4: Solution Design (Architecture Agent)
- [ ] Design targeted fix approach
- [ ] Assess fix impact and risks
- [ ] Plan rollout strategy
- [ ] Design prevention measures

### Phase 5: Implementation & Validation (All Agents)
- [ ] Implement fix with monitoring
- [ ] Validate fix effectiveness
- [ ] Test edge cases and regression
- [ ] Document solution and prevention

## Systematic Diagnostic Checklist
### Error Analysis
- [ ] **Error Logs**: Examined application logs for patterns
- [ ] **Network Traces**: Analyzed request/response flows
- [ ] **Database Queries**: Profiled slow/failing queries
- [ ] **Memory Usage**: Checked for memory leaks/spikes
- [ ] **Performance Metrics**: Reviewed response times/throughput
- [ ] **Security Logs**: Checked for security-related errors

### Environment Investigation
- [ ] **Infrastructure**: Server health and capacity
- [ ] **Dependencies**: Third-party service status
- [ ] **Configuration**: Environment-specific settings
- [ ] **Deployments**: Recent changes and rollouts
- [ ] **Data Integrity**: Database consistency checks
- [ ] **Monitoring**: Alert history and patterns

### Code Analysis
- [ ] **Recent Changes**: Git history for affected components
- [ ] **Code Review**: Logic errors and edge cases
- [ ] **Test Coverage**: Missing or inadequate tests
- [ ] **Dependencies**: Library version conflicts
- [ ] **Configuration**: Hardcoded values and settings
- [ ] **Error Handling**: Missing or inadequate error handling

## Root Cause Analysis Framework
### 5 Whys Analysis
1. **Why did the problem occur?**
   Answer: [First level cause]

2. **Why did [first level cause] happen?**
   Answer: [Second level cause]

3. **Why did [second level cause] happen?**
   Answer: [Third level cause]

4. **Why did [third level cause] happen?**
   Answer: [Fourth level cause]

5. **Why did [fourth level cause] happen?**
   Answer: [Root cause identified]

### Fishbone Diagram Categories
**People**: [Human factors contributing to issue]
**Process**: [Procedural gaps or failures]
**Technology**: [Technical system failures]
**Environment**: [Infrastructure or external factors]

### Contributing Factors Analysis
- **Primary Cause**: [Main technical/logical failure]
- **Secondary Causes**: [Factors that enabled primary cause]
- **Systemic Issues**: [Broader system weaknesses exposed]
- **Process Gaps**: [Missing safeguards or checks]

## Solution Design
### Fix Strategy Options
#### Option 1: [Quick Fix]
- **Approach**: [Description of quick resolution]
- **Pros**: [Benefits and speed to resolution]
- **Cons**: [Risks and long-term implications]
- **Effort**: [Time and resource requirements]

#### Option 2: [Comprehensive Fix]
- **Approach**: [Description of thorough resolution]
- **Pros**: [Long-term benefits and robustness]
- **Cons**: [Complexity and timeline]
- **Effort**: [Time and resource requirements]

#### Option 3: [Hybrid Approach]
- **Approach**: [Combination of immediate and long-term fixes]
- **Pros**: [Balance of speed and thoroughness]
- **Cons**: [Coordination complexity]
- **Effort**: [Phased implementation requirements]

### Selected Solution
**Chosen Approach**: [Selected option with rationale]
**Implementation Plan**: [Step-by-step execution plan]
**Risk Mitigation**: [How risks will be managed]
**Rollback Plan**: [How to revert if issues arise]

## MCP Server Integration for Debugging
### Required MCP Servers
- **filesystem**: Access to logs and configuration files
- **logging**: Centralized log analysis and pattern detection
- **debugging**: Runtime debugging and profiling tools
- **monitoring**: System metrics and health data

### Debugging Data Collection
```javascript
// MCP Server Usage for Debugging
const mcpLogging = await getMCPServer('logging');
const mcpMonitoring = await getMCPServer('monitoring');

// Collect comprehensive debugging data
const debugData = {
  logs: await mcpLogging.getLogsByTimeRange(startTime, endTime),
  metrics: await mcpMonitoring.getMetricsByComponent(componentName),
  traces: await mcpDebugging.getRequestTraces(transactionId)
};
```

## Anti-Patterns to Avoid
### Investigation Anti-Patterns
❌ **Jumping to Solutions**
- Always reproduce and understand before fixing
- Avoid assumptions based on similar past issues

❌ **Insufficient Root Cause Analysis**
- Don't stop at symptoms - find underlying causes
- Consider systemic issues, not just immediate triggers

❌ **Ignoring Environmental Factors**
- Check infrastructure, dependencies, configurations
- Consider timing, load, and external service issues

❌ **Poor Documentation of Process**
- Document investigation steps and findings
- Capture evidence and reasoning for future reference

### Solution Anti-Patterns
❌ **Quick Fixes Without Understanding**
- Understand the problem fully before implementing fixes
- Consider side effects and unintended consequences

❌ **Solving Symptoms, Not Causes**
- Address root causes to prevent recurrence
- Implement systemic improvements where needed

❌ **Introducing New Risks**
- Test fixes thoroughly before deployment
- Consider impact on other system components

❌ **Inadequate Prevention Measures**
- Implement monitoring and alerting improvements
- Add tests to prevent regression

## Implementation and Testing
### Fix Implementation Checklist
- [ ] Code changes implemented with proper testing
- [ ] Database migrations created if needed
- [ ] Configuration updates documented
- [ ] Deployment scripts updated
- [ ] Monitoring and alerting configured

### Testing Strategy
#### Unit Testing
- [ ] New tests for fixed functionality
- [ ] Edge cases that triggered the bug
- [ ] Error handling scenarios

#### Integration Testing
- [ ] End-to-end workflow testing
- [ ] Cross-component interaction testing
- [ ] Performance under normal load

#### Regression Testing
- [ ] Existing functionality unaffected
- [ ] Previous bug fixes still working
- [ ] System stability maintained

## Evidence Collection Requirements
### Investigation Evidence
- [ ] **Reproduction Steps**: Detailed steps to trigger issue
- [ ] **Error Logs**: Complete log excerpts with context
- [ ] **System State**: Screenshots, metrics, configurations
- [ ] **Timeline**: Sequence of events leading to issue

### Solution Evidence
- [ ] **Before/After Comparison**: Metrics and behavior changes
- [ ] **Test Results**: Unit, integration, and regression tests
- [ ] **Performance Impact**: Response times and resource usage
- [ ] **Monitoring Data**: Proof that issue is resolved

### Prevention Evidence
- [ ] **Monitoring Setup**: New alerts and dashboards
- [ ] **Test Coverage**: Additional tests to prevent regression
- [ ] **Documentation**: Updated troubleshooting guides
- [ ] **Process Improvements**: Enhanced development practices

## Prevention and Monitoring
### Immediate Prevention Measures
- [ ] **Monitoring**: Enhanced alerting for similar issues
- [ ] **Testing**: Additional test cases to catch regressions
- [ ] **Code Review**: Updated review checklist items
- [ ] **Documentation**: Troubleshooting guide updates

### Systemic Improvements
- [ ] **Architecture**: Design improvements to prevent issue class
- [ ] **Process**: Development process enhancements
- [ ] **Tools**: Better debugging and monitoring tools
- [ ] **Training**: Team knowledge sharing sessions

### Long-term Prevention Strategy
- [ ] **Pattern Recognition**: Automated detection of similar issues
- [ ] **Preventive Maintenance**: Regular system health checks
- [ ] **Capacity Planning**: Resource allocation improvements
- [ ] **Disaster Recovery**: Enhanced recovery procedures

## Success Validation Checklist
### Issue Resolution Validation
- [ ] Original issue no longer reproducible
- [ ] All reported symptoms resolved
- [ ] System performance restored to baseline
- [ ] No new issues introduced by fix

### Prevention Validation
- [ ] Monitoring alerts configured and tested
- [ ] Regression tests added and passing
- [ ] Team knowledge transfer completed
- [ ] Documentation updated and reviewed

### Quality Validation
- [ ] Code review completed and approved
- [ ] Testing coverage adequate for fix
- [ ] Performance impact acceptable
- [ ] Security implications assessed

## Post-Resolution Actions
### Immediate Actions
- [ ] **Status Communication**: Inform stakeholders of resolution
- [ ] **Monitoring Review**: Watch for any related issues
- [ ] **Documentation Update**: Update known issues database
- [ ] **Process Review**: Evaluate debugging process effectiveness

### Follow-up Actions
- [ ] **Trend Analysis**: Look for patterns with other issues
- [ ] **Process Improvement**: Enhance debugging procedures
- [ ] **Team Training**: Share lessons learned
- [ ] **Tool Enhancement**: Improve debugging capabilities

## Template Usage Notes
1. **Severity Triage**: Use severity levels to prioritize investigation depth
2. **Evidence Collection**: Document everything - assumptions often prove wrong
3. **Team Coordination**: Assign specific investigation roles to prevent overlap
4. **Prevention Focus**: Always implement measures to prevent recurrence
5. **Knowledge Sharing**: Ensure team learns from each debugging session

---
*Debugging Session Template v1.0 | TaylorDash Master AI Brains System*
```