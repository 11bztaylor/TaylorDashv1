# Security Policy

## Scope

TaylorDash is designed for local-only deployment in home/lab environments. However, we treat all secrets and credentials as production-level sensitive.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | ✅ Full support    |
| Latest tag | ✅ Full support |
| Older tags | ⚠️ Best effort   |

## Reporting a Security Vulnerability

### For Suspected Secret Leaks

If you discover secrets, tokens, or credentials in the repository:

1. **DO NOT** create a public issue
2. **Report via private issue** or email: security@taylordash.dev
3. Include:
   - File path and line number
   - Type of secret (API key, password, etc.)
   - Potential impact assessment

### For Security Vulnerabilities

Report security vulnerabilities privately via:
- **GitHub Private Vulnerability Reporting** (preferred)
- **Email**: security@taylordash.dev

Include:
- Vulnerability description
- Steps to reproduce
- Potential impact
- Suggested remediation (if known)

## Secret Leak Response

If a secret is confirmed in repository history:

### Immediate Actions
1. **Revoke the exposed secret** immediately
2. **Rotate credentials** (generate new secrets)
3. **History rewrite** to remove the secret

### History Rewrite Process
```bash
# Use git-filter-repo to remove secrets
git filter-repo --invert-paths --path 'path/to/secret/file'

# Force push (requires admin override)
git push origin --force-with-lease --all
```

Reference: [GitHub's guide to removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

### Post-Incident
1. Document the incident in security log
2. Review access controls and deployment procedures
3. Update `.gitignore` and secret detection rules
4. Team notification and training if applicable

## Security Best Practices

### Development
- **Never commit secrets** - use `.env.example` pattern
- **Use environment variables** for all sensitive configuration
- **Enable pre-commit hooks** for secret detection (gitleaks)
- **Regular security scans** of dependencies

### Deployment
- **Principle of least privilege** for service accounts
- **Network isolation** for sensitive services
- **Regular credential rotation** (quarterly minimum)
- **Audit logging** for administrative actions

### Monitoring
- **Failed authentication alerts** from services
- **Unusual access patterns** in logs
- **Regular security scan** results review
- **Dependency vulnerability** monitoring

## Acknowledgments

We appreciate security researchers who responsibly disclose vulnerabilities. Contributors will be acknowledged in release notes (unless they prefer anonymity).

## Contact

- **Security Issues**: security@taylordash.dev
- **General Contact**: @11bztaylor

---

**Remember**: Even in local deployments, security hygiene prevents habits that could be dangerous in production environments.