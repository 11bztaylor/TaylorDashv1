# Manual, deliberate Git backups

TaylorDash uses a deliberate, manual backup strategy with signed Git tags and validation gates.

## Backup Philosophy

- **Frequent local commits** → work is always saved locally
- **Manual backup push** → only when validation passes  
- **No background auto-push** → deliberate, conscious decision
- **Signed tags** → tamper-evident milestones
- **Validation-gated** → never push broken state

## Creating Backups

### Backup Checkpoint Examples

```bash
# Backup with signed tag
git tag -s v0.1.0 -m "checkpoint: phase-1 core"
git push origin v0.1.0

# Push current work
git push origin main

# Combined backup (using script)
./ops/backup_git.sh v0.1.0 "checkpoint: MQTT implementation complete"
```

### Manual Backup Process

If you prefer manual control:

```bash
# 1. Ensure working tree is clean
git status

# 2. Run validation (will exit if fails)
./ops/validate_p1.sh

# 3. Fetch latest from remote
git fetch origin

# 4. Create signed tag
git tag -s v0.1.0 -m "checkpoint: major milestone reached"

# 5. Push commits and tag
git push origin HEAD:main
git push origin v0.1.0

echo "Backup complete: HEAD and v0.1.0 pushed"
```

## Restore Examples

```bash
# Fetch all tags
git fetch --tags

# Restore to specific version
git checkout v0.1.0

# Create branch from backup
git checkout -b restore-v010 v0.1.0
```

## Multi-Component Backup Scripts

### Database Backups

```bash
# Run PostgreSQL backup to MinIO
./ops/backup_db.sh

# Backup specific database
./ops/backup_db.sh my_custom_db

# Example output:
# ✅ Backup complete!
#    MinIO Path: taylordash/db-backups/v0.1.0_20250910_143000.dump
#    Version ID: abc123def456
#    SHA256: a1b2c3d4e5f6...
```

### VictoriaMetrics Backups

```bash
# Run VM backup to MinIO
./ops/backup_vm.sh

# Example output:
# ✅ VictoriaMetrics backup complete!
#    MinIO Path: taylordash/vm-backups/v0.1.0_20250910_143000
#    Snapshot Used: 20250910143000-1A2B3C4D
```

## Restore Procedures

### PostgreSQL Restore

```bash
# Download backup from MinIO
mc cp taylordash/db-backups/v0.1.0_20250910_143000.dump ./restore.dump

# Verify checksum
sha256sum -c restore.dump.sha256

# Restore to new database
pg_restore -h localhost -U postgres -d taylordash_restored restore.dump

# Or restore via Docker
docker compose exec -T postgres pg_restore -U postgres -d taylordash_restored < restore.dump
```

### VictoriaMetrics Restore

```bash
# Restore VM data from MinIO backup
vmrestore -src="s3://minio:9000/taylordash/vm-backups/v0.1.0_20250910_143000" \
  -storageDataPath="/path/to/restored/vm-data" \
  -s3.accessKey="$MINIO_ROOT_USER" \
  -s3.secretKey="$MINIO_ROOT_PASSWORD"

# Or via Docker
docker run --rm -v vm_data_restored:/vm-data \
  victoriametrics/vmrestore:latest \
  -src="s3://minio:9000/taylordash/vm-backups/v0.1.0_20250910_143000" \
  -storageDataPath="/vm-data"
```

### MinIO Object Restore

```bash
# List object versions
mc ls --versions taylordash/docs/

# Download specific version
mc cp taylordash/docs/specs.pdf --version-id="abc123def456" ./specs_v1.pdf

# Verify SHA256 checksum
mc cat taylordash/docs/specs.pdf --version-id="abc123def456" | sha256sum

# Restore version as current
mc cp taylordash/docs/specs.pdf --version-id="abc123def456" taylordash/docs/specs.pdf
```

## Backup Triggers

Create backups at these milestones:

### Major Milestones
- ✅ **Infrastructure operational** (PR-01 complete)
- ✅ **Event system working** (PR-04 complete)  
- ✅ **Frontend functional** (PR-08 complete)
- ✅ **Production ready** (All PRs complete)

### Development Checkpoints
- **End of work session** (if significant progress)
- **Before major refactoring** (safety checkpoint)
- **After fixing critical bugs** (known good state)
- **Before deployment** (release candidate)

### ADR Milestones
Map important tags to Architecture Decision Records:

```bash
# Tag important architectural decisions
git tag -s v0.1.0-adr-001 -m "ADR-001: Event bus architecture finalized"
git tag -s v0.2.0-adr-005 -m "ADR-005: Multi-view UI implementation complete"
```

## Restore Procedures

### List Available Backups

```bash
# Show all tags with messages
git tag -l --sort=-version:refname

# Show tag details
git show v0.1.0

# Show commits for a tag
git log v0.1.0 --oneline -10
```

### Restore from Tag

```bash
# Create new branch from tag
git checkout -b restore-from-v010 v0.1.0

# Or reset current branch to tag (DESTRUCTIVE)
git reset --hard v0.1.0

# Or view specific files from tag
git show v0.1.0:docker-compose.yml
```

### Restore Specific Components

```bash
# Restore just the database schema
git checkout v0.1.0 -- backend/app/database.py

# Restore entire infrastructure config
git checkout v0.1.0 -- infra/

# Restore documentation to specific state
git checkout v0.1.0 -- docs/
```

## Disaster Recovery

### Complete Repository Loss

```bash
# Clone from GitHub
git clone git@github.com:11bztaylor/TaylorDashv1.git
cd TaylorDashv1

# Verify latest tag
git tag -l --sort=-version:refname | head -5

# Check out known good state
git checkout v0.1.0

# Rebuild environment
cp .env.example .env
# Edit .env with your secrets
make up
```

### Corrupted Working Directory

```bash
# Reset to last known good commit
git status
git reset --hard HEAD

# Or reset to specific tag
git reset --hard v0.1.0

# Clean untracked files
git clean -fd
```

### Lost Credentials

```bash
# Re-setup SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"
# Add public key to GitHub

# Re-setup signed commits
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
```

## Backup Verification

### After Each Backup

```bash
# Verify tag was pushed
git ls-remote --tags origin | grep v0.1.0

# Verify signature
git tag -v v0.1.0

# Test fresh clone
cd /tmp
git clone git@github.com:11bztaylor/TaylorDashv1.git test-clone
cd test-clone
git checkout v0.1.0
./ops/validate_p1.sh
```

### Monthly Verification

```bash
# Test full restore procedure
mkdir /tmp/disaster-recovery-test
cd /tmp/disaster-recovery-test
git clone git@github.com:11bztaylor/TaylorDashv1.git
cd TaylorDashv1

# Verify all tagged versions can be restored
for tag in $(git tag -l | head -5); do
  echo "Testing restore of $tag"
  git checkout $tag
  ./ops/validate_p1.sh || echo "WARN: $tag validation failed"
done

# Return to latest
git checkout main
```

## Tag Naming Convention

### Version Tags
```bash
v0.1.0    # Major milestone
v0.1.1    # Minor update  
v0.1.2    # Patch/bugfix
```

### Checkpoint Tags
```bash
v0.1.0-checkpoint-daily     # Daily backup
v0.1.0-milestone-mqtt       # Feature complete
v0.1.0-adr-001             # Architecture decision
v0.1.0-release-candidate   # Pre-production
```

### Emergency Tags
```bash
v0.1.0-before-refactor     # Safety before changes
v0.1.0-known-good         # Last working state
v0.1.0-emergency-backup   # Before risky operation
```

## Backup Storage Strategy

### Local Git Repository
- **All commits** preserved locally
- **Working tree** never lost
- **Local tags** for frequent checkpoints

### GitHub Remote  
- **Pushed commits** for off-site backup
- **Signed tags** for verified milestones
- **Protected main branch** prevents accidental overwrites

### Future Enhancements

Consider adding:

```bash
# Automated tag creation via release script
./ops/release_tag.sh minor "MQTT implementation complete"

# Database dump inclusion
git tag -s v0.1.0-with-data -m "Includes sample dataset"

# Configuration backup
tar -czf config-backup-$(date +%Y%m%d).tar.gz .env infra/
```

## Monitoring Backup Health

### Backup Cadence Check

```bash
# Show time since last backup
git log --oneline --since="1 week ago" origin/main

# Show unpushed commits
git log origin/main..HEAD --oneline

# Show untagged commits
git describe --tags --exact-match HEAD 2>/dev/null || echo "No tag on HEAD"
```

### Backup Size Monitoring

```bash
# Repository size
du -sh .git

# Large file detection
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '/^blob/ { if ($3 > 1048576) print $3, $4 }' | \
  sort -nr | head -10
```

## Recovery Testing

Test these scenarios monthly:

1. **Fresh clone** → works without issues
2. **Tag checkout** → specific version restores correctly  
3. **Validation passes** → all backups are functional
4. **Environment rebuild** → from `.env.example` to working system
5. **Credential recovery** → SSH keys and signed commits work

Document any issues and update procedures accordingly.

## Further Reading

- [Git Tagging](https://git-scm.com/book/en/v2/Git-Basics-Tagging)
- [Disaster Recovery Best Practices](https://docs.github.com/en/repositories/archiving-a-github-repository/backing-up-a-repository)
- [Git Reset Documentation](https://git-scm.com/docs/git-reset)