# Security Checklist

Comprehensive security checklist for TaylorDash development and deployment.

## 🔐 Repository Security

### Secrets Management

- [ ] **No secrets in repository**
  - [ ] All passwords/keys in `.env` (gitignored)
  - [ ] Configuration templates in `.env.example` (versioned)
  - [ ] gitleaks pre-commit hook active and passing
  - [ ] `.gitleaksignore` used only for documented false positives

- [ ] **Environment variable pattern enforced**
  ```bash
  # ✅ GOOD: .env.example (versioned)
  POSTGRES_PASSWORD=your_secure_password_here
  MINIO_ROOT_PASSWORD=change_this_password
  
  # ✅ GOOD: .env (gitignored)  
  POSTGRES_PASSWORD=actual_secure_password_123
  MINIO_ROOT_PASSWORD=real_minio_password_456
  
  # ❌ BAD: hardcoded in code
  DATABASE_URL = "postgresql://user:password123@localhost/db"
  ```

### Access Control

- [ ] **Repository permissions locked down**
  - [ ] Private repository (if not open source)
  - [ ] CODEOWNERS file requires review from `@11bztaylor`
  - [ ] Fine-grained Personal Access Tokens (if using HTTPS)
    - Scope: Single repository only
    - Permissions: Contents (read/write), Metadata (read), Pull requests (write)
    - Expiration: 90 days maximum

- [ ] **SSH key security**
  - [ ] Ed25519 keys preferred (`ssh-keygen -t ed25519`)
  - [ ] Passphrase-protected keys
  - [ ] Separate keys for different purposes (signing vs. auth)

## 🛡️ Git Security

### Branch Protection

Enable these settings on `main` branch:

- [ ] **Require a pull request before merging**
  - [ ] Require approvals: 1 minimum
  - [ ] Dismiss stale PR approvals when new commits are pushed
  - [ ] Require review from CODEOWNERS
  - [ ] Allow specified actors to bypass pull request requirements: ❌ (unchecked)

- [ ] **Require status checks to pass before merging**
  - [ ] Require branches to be up to date before merging
  - [ ] Status checks: `validate_p1` (when CI is configured)
  - [ ] Status checks: `pre-commit.ci` (if using pre-commit.ci)

- [ ] **Require signed commits**
- [ ] **Require linear history** 
- [ ] **Require deployments to succeed before merging** (future)
- [ ] **Lock branch** (for production releases)
- [ ] **Do not allow bypassing the above settings**

### Advanced Protection

- [ ] **Restrict pushes that create files**
  - Prevent accidental large file commits
  - Block executable uploads

- [ ] **Restrict force pushes** 
- [ ] **Restrict deletions**
- [ ] **Require conversation resolution before merging**

### Screenshots

Branch protection should look like this:

```
[✅] Require a pull request before merging
    [✅] Require approvals: 1
    [✅] Dismiss stale PR approvals when new commits are pushed  
    [✅] Require review from CODEOWNERS
    [❌] Allow specified actors to bypass pull request requirements

[✅] Require status checks to pass before merging
    [✅] Require branches to be up to date before merging
    Required status checks:
    [✅] validate_p1

[✅] Require signed commits
[✅] Require linear history
[✅] Do not allow bypassing the above settings
[✅] Restrict pushes that create files
[✅] Restrict force pushes  
[✅] Restrict deletions
```

## 🔑 Authentication Setup

### SSH Signing (Recommended)

```bash
# 1. Generate SSH key for signing
ssh-keygen -t ed25519 -C "signing-key-taylordash" -f ~/.ssh/id_ed25519_signing

# 2. Configure Git
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519_signing.pub
git config --global commit.gpgsign true

# 3. Add to GitHub
# Copy public key content:
cat ~/.ssh/id_ed25519_signing.pub
# GitHub → Settings → SSH and GPG keys → New SSH key → Signing key
```

### GPG Signing (Alternative)

```bash
# 1. Generate GPG key
gpg --full-generate-key
# Choose: RSA and RSA, 4096 bits, no expiration

# 2. Get key ID
gpg --list-secret-keys --keyid-format=long
# Look for: sec   rsa4096/YOUR_KEY_ID

# 3. Configure Git  
git config --global user.signingkey YOUR_KEY_ID
git config --global commit.gpgsign true

# 4. Export for GitHub
gpg --armor --export YOUR_KEY_ID
# GitHub → Settings → SSH and GPG keys → New GPG key
```

### Verification

```bash
# Test signed commit
git commit --allow-empty -m "test: verify signed commits"

# Check signature
git log --show-signature -1

# Should show: "Good signature from..."
```

## 🚨 Incident Response

### Secret Exposed in Repository

**IMMEDIATE ACTIONS:**

1. **Revoke the exposed secret**
   - Database passwords → change immediately
   - API keys → regenerate/revoke  
   - Certificates → revoke and reissue

2. **Remove from Git history**
   ```bash
   # Use git-filter-repo (install first)
   git filter-repo --invert-paths --path-glob '**/secret-file.env'
   
   # Force push (requires admin override)
   git push origin --force-with-lease --all
   ```

3. **Audit impact**
   - Check access logs for unauthorized usage
   - Scan for lateral movement
   - Update incident log

4. **Prevent recurrence**
   - Add pattern to `.gitleaksignore` with justification
   - Update `.gitignore` if needed
   - Team training on secret handling

### Compromised Developer Account

1. **Immediate containment**
   - Revoke GitHub Personal Access Tokens
   - Remove from repository collaborators
   - Disable compromised SSH keys

2. **Investigation**
   - Review Git log for suspicious commits
   - Check deployed systems for unauthorized changes
   - Audit access to secrets/infrastructure

3. **Recovery**
   - Reset all shared secrets
   - Re-deploy from known good state
   - Update access controls

## 📊 Security Monitoring

### Daily Checks (Automated)

- [ ] **gitleaks scan passes** (pre-commit hook)
- [ ] **No unsigned commits** (branch protection)
- [ ] **All PRs reviewed** (CODEOWNERS)
- [ ] **Status checks pass** (validate_p1.sh)

### Weekly Checks (Manual)

- [ ] **Review Git history for anomalies**
  ```bash
  # Check for unusual commit patterns
  git log --oneline --since="1 week ago" --author=".*" 
  
  # Check for unsigned commits
  git log --pretty="format:%h %G? %s" --since="1 week ago"
  # %G? should show 'G' for good signatures
  ```

- [ ] **Audit repository access**
  - Review GitHub collaborators
  - Check SSH keys and GPG keys
  - Verify Personal Access Token usage

- [ ] **Secret scanning results**
  ```bash
  # Run manual gitleaks scan
  gitleaks detect --source . --verbose
  
  # Check for new large files
  git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | awk '/^blob/ {if($3>1048576) print $3, $4}' | sort -nr
  ```

### Monthly Checks (Comprehensive)

- [ ] **Security tool updates**
  ```bash
  # Update pre-commit hooks
  pre-commit autoupdate
  pre-commit run --all-files
  ```

- [ ] **Access token rotation**
  - GitHub Personal Access Tokens → regenerate
  - SSH keys → rotate if > 1 year old  
  - GPG keys → check expiration

- [ ] **Branch protection audit**
  - Verify all protection rules active
  - Test bypass prevention
  - Check CODEOWNERS coverage

## 🔍 Security Validation

### Pre-deployment Checklist

- [ ] **gitleaks scan clean**
  ```bash
  gitleaks detect --source . --exit-code 1
  ```

- [ ] **No hardcoded secrets**
  ```bash
  grep -r "password\|secret\|key" --include="*.py" --include="*.yml" --exclude="*.example" .
  ```

- [ ] **All commits signed**
  ```bash
  git log --pretty="format:%h %G?" origin/main | grep -v "G$" | wc -l
  # Should return 0
  ```

- [ ] **Environment variables documented**
  ```bash
  # Verify .env.example covers all required variables
  grep "^[A-Z_]*=" .env.example | sort > /tmp/example_vars
  grep "getenv\|environ" backend/app/*.py | grep -o "[A-Z_]*" | sort -u > /tmp/code_vars
  diff /tmp/example_vars /tmp/code_vars
  ```

### Penetration Testing

Quarterly security assessment:

- [ ] **Dependency vulnerability scan**
  ```bash
  # Python dependencies
  cd backend && pip-audit
  
  # Node dependencies (when frontend added)
  cd frontend && npm audit
  ```

- [ ] **Container security scan**
  ```bash
  # Scan Docker images
  docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image taylordash-backend:latest
  ```

- [ ] **Configuration review**
  - Mosquitto broker security settings
  - PostgreSQL access controls  
  - MinIO bucket policies
  - Traefik security headers

## ⚖️ Compliance Requirements

### SOC 2 / ISO 27001 Alignment

- [ ] **Change management**
  - All changes via pull requests
  - Approval required from CODEOWNERS
  - Signed commits for non-repudiation

- [ ] **Access controls**
  - Principle of least privilege
  - Regular access reviews
  - Multi-factor authentication

- [ ] **Incident handling**
  - Documented response procedures
  - Security event logging
  - Post-incident reviews

### Audit Trail

Maintain these records:

- [ ] **Git history** (signed commits)
- [ ] **Access logs** (GitHub audit log)
- [ ] **Security scans** (gitleaks reports)
- [ ] **Incident reports** (security issues)
- [ ] **Training records** (security awareness)

## 📚 Security Resources

### Training Materials

- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Git Security Guide](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)
- [Secret Scanning Tools](https://github.com/gitleaks/gitleaks)

### Emergency Contacts

- **Repository Owner**: @11bztaylor
- **GitHub Support**: https://support.github.com/
- **Security Issues**: security@yourdomain.com

### Quick Reference

```bash
# Emergency secret removal
git filter-repo --invert-paths --path 'path/to/secret/file'

# Force signature verification
git config --global commit.gpgsign true

# Audit recent commits
git log --show-signature --since="1 week ago"

# Check branch protection
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/11bztaylor/TaylorDashv1/branches/main/protection
```

Remember: **Security is a process, not a one-time setup. Regular reviews and updates are essential.**