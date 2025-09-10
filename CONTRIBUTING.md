# Contributing to TaylorDash

## Commit Style

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>
```

**Types:** `feat`, `fix`, `docs`, `chore`, `refactor`, `perf`, `test`, `build`, `ci`

**Examples:**
```bash
git commit -m "feat(ui): add multi-view tabs"
git commit -m "fix(api): resolve timeout issue"
git commit -m "docs(readme): update setup guide"
```

**Breaking Changes:** Add `!` after type or use `BREAKING CHANGE:` footer.

This maps to [Semantic Versioning 2.0.0](https://semver.org/):
- `feat` → MINOR version bump
- `fix` → PATCH version bump  
- `feat!` or `BREAKING CHANGE` → MAJOR version bump

## Branch Naming

- `feat/<area>-<slug>` (e.g., `feat/core-reactflow`)
- `fix/<area>-<slug>` (e.g., `fix/api-timeout`)

## Pull Request Etiquette

- **Link issue** in PR description
- **Summarize change** (what & why)
- **Pass local validation** before pushing
- **Update docs/ADRs** when interfaces change
- **Include schema diff** for API/event changes

## Reviewer Expectations

- Review for correctness and design
- Check that validation passes locally
- Verify docs are updated
- Confirm ADRs reflect API changes

## Repository Rules

The repository may enforce [branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches) and require [signed commits](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits). See GitHub settings for current rules.

## Code Ownership

CODEOWNERS file auto-requests reviews from designated maintainers. All changes require approval before merging.