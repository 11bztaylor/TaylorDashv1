# Contributing to TaylorDash

## Commit Style (REQUIRED)

**Conventional Commits are REQUIRED** - all commits must follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>
```

### Valid Examples
```bash
✅ git commit -m "feat(ui): add multi-view tabs"
✅ git commit -m "fix(api): resolve timeout issue"  
✅ git commit -m "docs(readme): update setup guide"
✅ git commit -m "feat(mqtt)!: change event schema format"
✅ git commit -m "chore: update dependencies"
```

### Invalid Examples
```bash
❌ git commit -m "Update README"
❌ git commit -m "Fixed bug"
❌ git commit -m "WIP: working on feature"
❌ git commit -m "Merge pull request #123"
```

**Types:** `feat`, `fix`, `docs`, `chore`, `refactor`, `perf`, `test`, `build`, `ci`

**Breaking Changes:** Add `!` after type or use `BREAKING CHANGE:` footer.

### SemVer Mapping
This maps to [Semantic Versioning 2.0.0](https://semver.org/):
- **MAJOR** (breaking changes): `feat!`, `fix!`, or `BREAKING CHANGE:` footer
- **MINOR** (new features): `feat` commits
- **PATCH** (bug fixes): `fix` commits

## Branch Naming

- `feat/<area>-<slug>` (e.g., `feat/core-reactflow`)
- `fix/<area>-<slug>` (e.g., `fix/api-timeout`)

## Pull Request Requirements

**No direct pushes to main** - use short-lived feature branches and pull requests only.

- **Link issue** in PR description
- **Summarize change** (what & why)
- **Pass local validation** (`ops/validate_p1.sh`) before pushing
- **Update docs/ADRs** when interfaces change
- **ADR required** if API/event schemas change
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