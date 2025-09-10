# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Finalization and validation pack with governance files
- SECURITY.md with incident response procedures
- LICENSE (Apache-2.0) with patent grant
- Enhanced issue templates with component selection
- Repository audit and validation scripts
- Observability documentation with metrics exposition
- Versioning guidance and backup scripts
- Documentation versioning with Mike
- MinIO object versioning configuration  
- PostgreSQL and VictoriaMetrics backup procedures

### Changed
- Enhanced CONTRIBUTING.md with valid/invalid commit examples
- Enhanced backup-restore documentation with multi-component strategy
- Updated PR template to require Conventional Commits validation

## [0.1.0] - 2025-09-10

### Added
- Initial TaylorDash implementation with event-driven architecture
- MQTT message bus with Mosquitto broker
- Async MQTT client with reconnect and exponential backoff
- Dead Letter Queue (DLQ) handling for failed events
- PostgreSQL database with connection pooling and migrations
- Event schema validation with JSON Schema
- Prometheus metrics exposition at `/metrics` endpoint
- OpenTelemetry instrumentation for distributed tracing
- Docker Compose infrastructure with health checks
- Comprehensive Git hygiene with pre-commit hooks
- gitleaks secret detection and conventional commit validation
- GitHub PR/issue templates and CODEOWNERS configuration
- Manual deliberate backup strategy with signed Git tags
- Validation scripts and comprehensive documentation

### Security
- Zero secrets in repository policy with .env.example pattern
- Pre-commit hooks for secret detection and code quality
- Signed commit requirements and branch protection guidance

[Unreleased]: https://github.com/11bztaylor/TaylorDashv1/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/11bztaylor/TaylorDashv1/releases/tag/v0.1.0