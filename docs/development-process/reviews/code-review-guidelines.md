# Code Review Guidelines

**Last Updated:** 2025-09-12
**Version:** 1.0
**Status:** Based on 89% test pass rate analysis

## Review Priorities

### Critical Review Areas
1. **Authentication & Security** - Zero tolerance for security issues
2. **API Contract Compliance** - Zero breaking changes allowed
3. **Database Schema Changes** - Migration impact assessment
4. **Plugin Security** - Sandboxing and permission validation
5. **Performance Impact** - Sub-second response requirement

## Security Review Checklist

### Authentication Changes
- [ ] Password hashing uses bcrypt with proper salt
- [ ] Session tokens cryptographically secure (32-byte random)
- [ ] Token expiration properly enforced
- [ ] Role-based access control maintained
- [ ] API key validation unchanged

### Input Validation
- [ ] Pydantic schemas validate all inputs
- [ ] SQL injection protection via parameterized queries
- [ ] XSS prevention through proper encoding
- [ ] CORS configuration reviewed
- [ ] File upload restrictions enforced

### Plugin Security
- [ ] Sandboxing mechanisms intact
- [ ] Permission system enforced
- [ ] Security scanning for new plugins
- [ ] Violation tracking functional
- [ ] Isolation boundaries maintained

## API Review Process

### Contract Validation
```bash
# Generate current API spec
curl http://localhost:3000/openapi.json > current_spec.json

# Compare with baseline
diff baseline_openapi.json current_spec.json

# Validate no breaking changes
python tools/api_contract_validator.py
```

### Endpoint Security Review
- [ ] Authentication requirements documented
- [ ] Authorization levels specified (API key vs JWT)
- [ ] Rate limiting considerations
- [ ] Input validation schemas complete
- [ ] Error response formats consistent

### Response Schema Review
- [ ] No sensitive data exposed
- [ ] Pagination implemented for lists
- [ ] Timestamps in ISO 8601 format
- [ ] Error messages user-friendly
- [ ] Status codes semantically correct

## Performance Review Guidelines

### Response Time Targets
- **API Endpoints:** < 500ms average, < 200ms P95
- **Database Queries:** < 100ms simple, < 500ms complex
- **Frontend Load:** < 1 second initial
- **MQTT Processing:** < 50ms event handling

### Performance Review Checklist
- [ ] Database queries optimized (explain plans reviewed)
- [ ] Connection pooling not exceeded
- [ ] Memory usage patterns analyzed
- [ ] Resource cleanup implemented
- [ ] Caching strategies appropriate

### Load Testing Requirements
```bash
# API load test (must pass)
ab -n 100 -c 10 -H 'Host: taylordash.local' http://localhost/api/v1/projects

# Database connection test
for i in {1..50}; do curl -s http://localhost:3000/api/v1/projects > /dev/null & done
wait
```

## Database Review Process

### Schema Changes
- [ ] Migration scripts idempotent
- [ ] Backward compatibility maintained
- [ ] Index performance impact assessed
- [ ] Data integrity constraints preserved
- [ ] Rollback procedures documented

### Query Review
- [ ] Proper indexing for new queries
- [ ] N+1 query problems avoided
- [ ] Transaction boundaries appropriate
- [ ] Connection lifecycle managed
- [ ] Error handling implemented

## Frontend Review Guidelines

### Component Quality
- [ ] React best practices followed
- [ ] State management appropriate
- [ ] Error boundaries implemented
- [ ] Loading states handled
- [ ] Accessibility considerations

### UI/UX Review
- [ ] Responsive design maintained
- [ ] Dark theme consistency
- [ ] Navigation patterns preserved
- [ ] Error handling user-friendly
- [ ] Performance optimized

### Security Frontend Review
- [ ] Authentication state managed securely
- [ ] Sensitive data not exposed in client
- [ ] HTTPS enforced for production
- [ ] Content Security Policy compliant
- [ ] XSS prevention measures active

## Plugin Development Review

### Security Assessment
- [ ] Plugin isolation verified
- [ ] Permission system enforced
- [ ] Security scanning passed
- [ ] Malicious code detection clear
- [ ] Resource limits enforced

### Architecture Review
- [ ] Plugin API compliance
- [ ] Event bus usage appropriate
- [ ] Configuration schema valid
- [ ] Health check implementation
- [ ] Documentation complete

## Testing Review Requirements

### Test Coverage
- [ ] Unit tests for new functionality
- [ ] Integration tests for API changes
- [ ] End-to-end tests for user flows
- [ ] Security tests for auth changes
- [ ] Performance tests for critical paths

### Test Quality
- [ ] Tests are deterministic
- [ ] Proper setup/teardown
- [ ] Meaningful assertions
- [ ] Edge cases covered
- [ ] Error conditions tested

## Review Process Workflow

### Pre-Review Preparation
1. **Automated Checks:** All CI/CD checks passing
2. **Test Validation:** `./ops/validate_p1.sh` passes (89%+)
3. **Security Scan:** No new vulnerabilities
4. **Performance Test:** Response times within limits
5. **Documentation:** Changes documented

### Review Steps
1. **Architecture Review** (30 minutes max)
   - Design patterns appropriate
   - System boundaries respected
   - Integration points validated

2. **Security Review** (45 minutes max)
   - Authentication/authorization correct
   - Input validation comprehensive
   - Security headers present

3. **Code Quality Review** (30 minutes max)
   - Code standards followed
   - Error handling appropriate
   - Documentation adequate

4. **Testing Review** (15 minutes max)
   - Test coverage sufficient
   - Test quality acceptable
   - Integration tests pass

### Approval Criteria
- [ ] All automated checks pass
- [ ] Security review approved
- [ ] Performance benchmarks met
- [ ] API contracts maintained
- [ ] Documentation updated

## Review Tools

### Automated Analysis
```bash
# Code quality analysis
flake8 backend/
black --check backend/
mypy backend/

# Security scanning
bandit -r backend/
safety check

# Test coverage
pytest --cov=backend backend/tests/
```

### Manual Review Tools
- **API Testing:** Postman/Thunder Client collections
- **Database Review:** pgAdmin for query analysis
- **Frontend Review:** Browser dev tools
- **Performance:** Chrome DevTools, Lighthouse
- **Security:** OWASP ZAP for vulnerability scanning

## Common Review Issues

### Frequent Problems
1. **Missing Input Validation** - All user inputs must be validated
2. **Inadequate Error Handling** - Graceful degradation required
3. **Performance Regressions** - Monitor response time impact
4. **Security Headers Missing** - Required for all responses
5. **Test Coverage Gaps** - Critical paths must be tested

### Red Flags
- **Hardcoded Credentials** - Immediate rejection
- **SQL String Concatenation** - SQL injection risk
- **Unvalidated User Input** - XSS/injection vulnerability
- **Missing Authentication** - Security boundary violation
- **Breaking API Changes** - Contract violation

## Review Timeline

### Standard Review
- **Simple Changes:** 2-4 hours
- **Medium Changes:** 1 business day
- **Complex Changes:** 2-3 business days
- **Security Changes:** Priority review (same day)

### Expedited Review Criteria
- Critical security fixes
- Production hotfixes
- Zero-impact changes (documentation only)
- Automated dependency updates (after validation)

## Post-Review Process

### Merge Requirements
- [ ] All reviewer feedback addressed
- [ ] Final validation passes
- [ ] Performance impact documented
- [ ] Deployment plan approved
- [ ] Rollback procedure documented

### Post-Merge Validation
- [ ] Deployment successful
- [ ] Health checks passing
- [ ] Performance metrics stable
- [ ] Error rates unchanged
- [ ] User experience unaffected