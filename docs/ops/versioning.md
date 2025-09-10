# Versioning Strategy

TaylorDash uses comprehensive versioning across all components: Git tags, documentation, object storage, databases, and time-series data.

## Git Releases

### Creating Signed Tags

```bash
# Create signed tag with message
git tag -s v0.1.0 -m "Release v0.1.0: MQTT implementation complete"

# Push tag to origin
git push origin v0.1.0

# List tags with verification
git tag -v v0.1.0
```

### GitHub Releases

Create releases tied to tags via [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository):

1. Navigate to repository → Releases → Create a new release
2. Choose existing tag (e.g., `v0.1.0`) 
3. Generate release notes from commits
4. Publish release

## SemVer + Conventional Commits

We follow [Semantic Versioning 2.0.0](https://semver.org/) with [Conventional Commits](https://www.conventionalcommits.org/) mapping:

### Version Bump Rules

- **MAJOR** (breaking changes): `feat!`, `fix!`, or `BREAKING CHANGE:` footer
- **MINOR** (new features): `feat:` commits
- **PATCH** (bug fixes): `fix:` commits

### Examples

```bash
# PATCH: v0.1.0 → v0.1.1
git commit -m "fix(api): resolve timeout in health check"

# MINOR: v0.1.1 → v0.2.0  
git commit -m "feat(mqtt): add DLQ retry mechanism"

# MAJOR: v0.2.0 → v1.0.0
git commit -m "feat(api)!: change event schema to include version field"

# MAJOR (alternative): v1.0.0 → v2.0.0
git commit -m "feat(core): redesign event bus architecture

BREAKING CHANGE: Event payload format changed from flat to nested structure"

# PATCH: v2.0.0 → v2.0.1
git commit -m "docs(readme): fix installation command typo"
```

## Documentation Versioning with Mike

### Setup

```bash
# Install mike for MkDocs versioning
pip install mkdocs-material mike

# Deploy version to GitHub Pages
mike deploy --push --update-aliases 0.1 latest

# Set default version
mike set-default --push latest

# List all versions
mike list
```

### Workflow

```bash
# Deploy new version
mike deploy --push --update-aliases 0.2 latest

# Deploy development docs
mike deploy --push dev

# Serve locally with version selector
mike serve
```

## MinIO Object Versioning

### Enable Versioning

```bash
# Enable versioning on buckets
mc version enable taylordash/docs
mc version enable taylordash/briefs

# Verify versioning status
mc version info taylordash/docs
```

### Managing Versions

```bash
# List object versions
mc ls --versions taylordash/docs/

# Download specific version
mc cp taylordash/docs/file.pdf --version-id="VERSION_ID" ./file.pdf

# Restore specific version (make it current)
mc cp taylordash/docs/file.pdf --version-id="VERSION_ID" taylordash/docs/file.pdf
```

### Example Output

```bash
$ mc ls --versions taylordash/docs/
[2025-01-15 10:30:00 UTC] 1.2MiB specs.pdf (version-id: abc123def456)
[2025-01-15 09:15:00 UTC] 1.1MiB specs.pdf (version-id: def456abc123)
[2025-01-14 16:45:00 UTC] 1.0MiB specs.pdf (version-id: 789xyz321abc)
```

## PostgreSQL Backups

### Logical Backups

```bash
# Create compressed logical backup
pg_dump -h localhost -U postgres -d taylordash -Fc -f backup_$(date +%Y%m%d_%H%M%S).dump

# Restore from backup
pg_restore -h localhost -U postgres -d taylordash_restored backup_20250115_103000.dump

# Backup specific tables
pg_dump -h localhost -U postgres -d taylordash -Fc -t events_mirror -t dlq_events -f events_backup.dump
```

### Point-in-Time Recovery (PITR)

For time travel capabilities, see [PostgreSQL PITR Documentation](https://www.postgresql.org/docs/current/continuous-archiving.html).

## VictoriaMetrics Backups

### vmbackup to MinIO

```bash
# Backup VM data to MinIO
vmbackup -storageDataPath=/victoria-metrics-data \
  -dst=s3://minio:9000/taylordash/vm-backups/$(date +%Y%m%d_%H%M%S) \
  -s3.accessKey="${MINIO_ROOT_USER}" \
  -s3.secretKey="${MINIO_ROOT_PASSWORD}"

# Restore from MinIO backup
vmrestore -src=s3://minio:9000/taylordash/vm-backups/20250115_103000 \
  -storageDataPath=/victoria-metrics-data-restored \
  -s3.accessKey="${MINIO_ROOT_USER}" \
  -s3.secretKey="${MINIO_ROOT_PASSWORD}"
```

### Automated Backups with vmbackupmanager

```bash
# Run vmbackupmanager for scheduled backups
vmbackupmanager -dst=s3://minio:9000/taylordash/vm-backups \
  -storageDataPath=/victoria-metrics-data \
  -snapshot.createURL=http://victoriametrics:8428/snapshot/create \
  -snapshot.deleteURL=http://victoriametrics:8428/snapshot/delete \
  -s3.accessKey="${MINIO_ROOT_USER}" \
  -s3.secretKey="${MINIO_ROOT_PASSWORD}" \
  -retention=30d
```

See [VictoriaMetrics Backup Documentation](https://docs.victoriametrics.com/vmbackup.html) for detailed configuration.

## Keep a Changelog

We follow [Keep a Changelog](https://keepachangelog.com/) format for `CHANGELOG.md`:

### Format Structure

```markdown
# Changelog

## [Unreleased]
### Added
- New features

### Changed  
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security improvements

## [1.0.0] - 2025-01-15
### Added
- Initial release with MQTT event bus
- PostgreSQL data persistence
- VictoriaMetrics time-series storage
```

### Linking to Releases

```markdown
[Unreleased]: https://github.com/11bztaylor/TaylorDashv1/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/11bztaylor/TaylorDashv1/releases/tag/v1.0.0
```

## Version Verification

### SHA256 Checksums

```bash
# Generate checksum for release artifacts
sha256sum backup_20250115_103000.dump > backup_20250115_103000.dump.sha256

# Verify checksum
sha256sum -c backup_20250115_103000.dump.sha256
```

### MinIO Object Integrity

```bash
# Get object metadata including ETag
mc stat taylordash/docs/specs.pdf --version-id="abc123def456"

# Compare checksums
mc cat taylordash/docs/specs.pdf --version-id="abc123def456" | sha256sum
```

## Backup Coordination

### Release Workflow

1. **Code ready**: All tests pass, docs updated
2. **Create backups**: Run `ops/backup_db.sh` and `ops/backup_vm.sh`
3. **Tag release**: `git tag -s v0.1.0 -m "Release v0.1.0"`
4. **Deploy docs**: `mike deploy --push --update-aliases 0.1 latest`
5. **Push tag**: `git push origin v0.1.0`
6. **Create GitHub Release**: Link to tag with release notes

### Disaster Recovery

1. **Restore Git**: `git clone` and `git checkout v0.1.0`
2. **Restore Database**: `pg_restore` from MinIO backup
3. **Restore Metrics**: `vmrestore` from MinIO backup  
4. **Restore Objects**: `mc cp` specific versions from MinIO
5. **Verify Integrity**: Check SHA256 checksums

This comprehensive versioning strategy ensures every component can be restored to any point in time.