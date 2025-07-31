# Git Workflow Strategy for FoodXchange

## Branch Strategy

### Main Branches
- **`main`** - Development branch (default)
- **`staging`** - Pre-production testing
- **`production`** - Production deployment (protected)

### Feature Branches
- **`feature/*`** - New features
- **`bugfix/*`** - Bug fixes
- **`hotfix/*`** - Emergency production fixes

## Workflow

```
feature/* → main → staging → production
```

### 1. Development Flow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Work on feature
git add .
git commit -m "feat: add new feature"

# Push to GitHub
git push origin feature/new-feature

# Create PR to main
```

### 2. Staging Deployment
```bash
# After PR merged to main
git checkout staging
git merge main
git push origin staging

# GitHub Actions automatically deploys to staging
```

### 3. Production Deployment
```bash
# After testing on staging
git checkout production
git merge staging
git push origin production

# GitHub Actions waits for manual approval
# Approve in GitHub UI → Deploys to production
```

## Branch Protection Rules

### Production Branch
- Require pull request reviews (2 approvers)
- Require status checks to pass
- Require branches to be up to date
- Include administrators
- Restrict who can push

### Staging Branch
- Require pull request reviews (1 approver)
- Require status checks to pass

## Commit Message Convention

```
type(scope): description

[optional body]

[optional footer]
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/maintenance tasks

### Examples:
```bash
git commit -m "feat(auth): add OAuth2 authentication"
git commit -m "fix(search): resolve timeout issues"
git commit -m "docs: update deployment instructions"
```

## Emergency Hotfix Process

```bash
# Create hotfix from production
git checkout production
git checkout -b hotfix/critical-fix

# Fix issue
git add .
git commit -m "hotfix: fix critical bug"

# Merge to production (with approval)
git checkout production
git merge hotfix/critical-fix
git push origin production

# Backport to staging and main
git checkout staging
git merge hotfix/critical-fix
git push origin staging

git checkout main
git merge hotfix/critical-fix
git push origin main
```