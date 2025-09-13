# Git Workflow and Branching Strategy

**Last Updated:** 2025-09-12
**Version:** 1.0
**Status:** Production Ready Development Process

## Branching Strategy

### Main Branches
- **`main`** - Production-ready code, always deployable
- **`develop`** - Integration branch for features
- **`release/v*`** - Release preparation branches
- **`hotfix/*`** - Critical production fixes

### Feature Branches
- **`feature/*`** - New features and enhancements
- **`bugfix/*`** - Bug fixes for development
- **`security/*`** - Security-related changes
- **`performance/*`** - Performance improvements

## Git Flow Process

### Feature Development
```bash
# Start feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/authentication-improvements

# Work on feature
git add .
git commit -m "Add JWT session management

- Implement secure session token generation
- Add database-backed session storage
- Configure proper token expiration

🤖 Generated with Claude Code"

# Push feature branch
git push -u origin feature/authentication-improvements
```

### Code Review Process
```bash
# Create pull request
gh pr create --title "Add JWT Authentication System" --body "
## Summary
- Implement secure JWT-based authentication
- Add role-based access control
- Maintain API key compatibility

## Test plan
- [ ] Authentication flow tested
- [ ] API contracts validated
- [ ] Performance benchmarks met
- [ ] Security review completed

🤖 Generated with Claude Code"

# Address review feedback
git add .
git commit -m "Address review feedback: improve error handling"
git push origin feature/authentication-improvements
```

### Integration to Develop
```bash
# Merge to develop after approval
git checkout develop
git pull origin develop
git merge --no-ff feature/authentication-improvements
git push origin develop

# Delete feature branch
git branch -d feature/authentication-improvements
git push origin --delete feature/authentication-improvements
```

## Release Management

### Release Preparation
```bash
# Create release branch
git checkout develop
git pull origin develop
git checkout -b release/v1.1.0

# Update version information
echo "VERSION=1.1.0" >> .env
git add .env
git commit -m "Bump version to 1.1.0 for release"

# Final testing and bug fixes
./ops/validate_p1.sh
# Fix any issues found
```

### Release Finalization
```bash
# Merge to main
git checkout main
git pull origin main
git merge --no-ff release/v1.1.0

# Tag release
git tag -a v1.1.0 -m "Release version 1.1.0

Features:
- Enhanced authentication system
- Improved plugin security
- Performance optimizations

🤖 Generated with Claude Code"

git push origin main
git push origin v1.1.0

# Merge back to develop
git checkout develop
git merge --no-ff release/v1.1.0
git push origin develop

# Clean up release branch
git branch -d release/v1.1.0
git push origin --delete release/v1.1.0
```

## Hotfix Process

### Emergency Fixes
```bash
# Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix

# Apply fix
git add .
git commit -m "Fix critical security vulnerability in auth

- Patch session token validation
- Add additional input sanitization
- Update security headers

🤖 Generated with Claude Code"

# Test hotfix
./ops/validate_p1.sh

# Merge to main
git checkout main
git merge --no-ff hotfix/critical-security-fix
git tag -a v1.1.1 -m "Hotfix v1.1.1: Critical security patch"
git push origin main
git push origin v1.1.1

# Merge to develop
git checkout develop
git merge --no-ff hotfix/critical-security-fix
git push origin develop

# Clean up
git branch -d hotfix/critical-security-fix
git push origin --delete hotfix/critical-security-fix
```

## Commit Message Standards

### Commit Message Format
```
<type>: <subject line>

<body>

🤖 Generated with Claude Code
```

### Commit Types
- **feat:** New features
- **fix:** Bug fixes
- **security:** Security improvements
- **perf:** Performance optimizations
- **refactor:** Code refactoring
- **test:** Testing changes
- **docs:** Documentation updates
- **style:** Code formatting changes
- **chore:** Build process or auxiliary tool changes

### Good Commit Examples
```bash
# Feature commit
git commit -m "feat: add JWT authentication system

- Implement secure session token generation
- Add database-backed session storage
- Configure role-based access control
- Maintain backward compatibility with API keys

Tested with ./ops/validate_p1.sh (89% pass rate)

🤖 Generated with Claude Code"

# Bug fix commit
git commit -m "fix: resolve MQTT connection timeout issues

- Increase connection timeout to 30 seconds
- Add connection retry logic with exponential backoff
- Improve error handling and logging

Fixes intermittent connection failures observed in production.

🤖 Generated with Claude Code"

# Security commit
git commit -m "security: strengthen password hashing

- Upgrade bcrypt rounds from 10 to 12
- Add password complexity validation
- Implement account lockout after failed attempts

Addresses security audit recommendations.

🤖 Generated with Claude Code"
```

## Pre-commit Hooks

### Pre-commit Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: local
    hooks:
      - id: validate-system
        name: System Validation
        entry: ./ops/validate_p1.sh
        language: system
        pass_filenames: false
        always_run: true
```

### Install Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Skip hooks if needed (emergency only)
git commit -m "emergency fix" --no-verify
```

## Code Review Guidelines

### Pull Request Template
```markdown
## Summary
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Security improvement
- [ ] Performance optimization
- [ ] Documentation update

## Test Plan
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] ./ops/validate_p1.sh passes (89%+)
- [ ] Manual testing completed
- [ ] Performance impact assessed

## Security Checklist
- [ ] No hardcoded secrets or credentials
- [ ] Input validation implemented
- [ ] Authentication/authorization appropriate
- [ ] SQL injection prevention verified
- [ ] XSS prevention measures in place

## Performance Impact
- [ ] Response times maintained
- [ ] Memory usage stable
- [ ] Database queries optimized
- [ ] No resource leaks introduced

## Documentation
- [ ] Code comments updated
- [ ] API documentation updated
- [ ] User documentation updated (if applicable)
- [ ] Deployment notes provided (if applicable)

🤖 Generated with Claude Code
```

### Review Checklist
- [ ] Code quality and style
- [ ] Security considerations
- [ ] Performance impact
- [ ] Test coverage adequate
- [ ] Documentation updated
- [ ] API contracts maintained
- [ ] Error handling appropriate
- [ ] Logging sufficient

## Continuous Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Start services
      run: |
        docker-compose up -d
        sleep 60

    - name: Run validation
      run: |
        ./ops/validate_p1.sh

    - name: Run tests
      run: |
        docker-compose exec -T backend pytest
        cd frontend && npm test

    - name: Security scan
      run: |
        docker run --rm -v $(pwd):/src aquasec/trivy:latest fs /src

    - name: Performance test
      run: |
        ab -n 100 -c 10 http://localhost:3000/api/v1/projects
```

## Repository Management

### Branch Protection Rules
```bash
# Configure branch protection via GitHub CLI
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["CI/CD Pipeline"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":2,"dismiss_stale_reviews":true}' \
  --field restrictions=null
```

### Release Management
```bash
# Automated release creation
gh release create v1.1.0 \
  --title "TaylorDash v1.1.0" \
  --notes "
## Features
- Enhanced authentication system
- Improved plugin security
- Performance optimizations

## API Changes
- No breaking changes
- New authentication endpoints added

## Security
- Strengthened password hashing
- Enhanced session management
- Improved input validation

🤖 Generated with Claude Code"
```

## Development Environment

### Local Development Setup
```bash
# Clone repository
git clone https://github.com/your-org/TaylorDashv1.git
cd TaylorDashv1

# Set up development environment
cp .env.example .env
make setup

# Start development services
make dev

# Run validation
./ops/validate_p1.sh
```

### Development Best Practices
- [ ] Always work on feature branches
- [ ] Keep commits atomic and focused
- [ ] Write descriptive commit messages
- [ ] Test changes before committing
- [ ] Update documentation with changes
- [ ] Follow code style guidelines
- [ ] Run pre-commit hooks

## Troubleshooting Git Issues

### Common Problems
```bash
# Sync with remote after force push
git fetch origin
git reset --hard origin/main

# Resolve merge conflicts
git status
git add resolved_file.py
git commit -m "Resolve merge conflict in resolved_file.py"

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Rewrite commit message
git commit --amend -m "New commit message"

# Clean up local branches
git branch --merged | grep -v main | grep -v develop | xargs git branch -d
```

### Recovery Procedures
```bash
# Recover lost commits
git reflog
git checkout <lost-commit-hash>
git branch recovered-work

# Fix accidental main push
git checkout main
git reset --hard origin/main
git push --force-with-lease origin main

# Recover deleted branch
git reflog --all | grep branch-name
git checkout -b branch-name <commit-hash>
```