#!/bin/bash
# GitHub Repository Cleanup Script
# This script will clean up your GitHub repository completely

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
REPO_NAME="foodxchange"
GITHUB_USER=$(git config user.name)

echo -e "${BLUE}=== GitHub Repository Cleanup Script ===${NC}"
echo -e "${YELLOW}Repository: $REPO_NAME${NC}"
echo -e "${YELLOW}User: $GITHUB_USER${NC}"
echo ""

# Function to confirm action
confirm() {
    read -p "$1 (y/N): " response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# 1. List and clean branches
echo -e "${GREEN}Step 1: Branch Cleanup${NC}"
echo "Current branches:"
git branch -a

echo ""
echo "Remote branches:"
git ls-remote --heads origin

if confirm "Do you want to delete old branches (keeping only main)?"; then
    # Delete local branches except main
    git branch | grep -v "main" | xargs -r git branch -D 2>/dev/null || true
    
    # Delete remote branches except main, staging, and production
    git branch -r | grep -v "main\|staging\|production\|HEAD" | sed 's/origin\///' | xargs -r -I {} git push origin --delete {} 2>/dev/null || true
    
    echo -e "${GREEN}✓ Branches cleaned${NC}"
fi

# 2. Clean GitHub Actions artifacts
echo -e "${GREEN}Step 2: GitHub Actions Cleanup${NC}"
if command -v gh &> /dev/null; then
    echo "Cleaning workflow runs..."
    
    # List workflow runs
    gh run list --limit 100 --json databaseId,status,conclusion | jq -r '.[] | "\(.databaseId) \(.status) \(.conclusion)"'
    
    if confirm "Delete all workflow runs?"; then
        gh run list --limit 100 --json databaseId -q '.[].databaseId' | xargs -I {} gh run delete {} 2>/dev/null || true
        echo -e "${GREEN}✓ Workflow runs deleted${NC}"
    fi
    
    # Clean artifacts
    echo "Cleaning artifacts..."
    gh api repos/:owner/:repo/actions/artifacts --jq '.artifacts[].id' | xargs -I {} gh api -X DELETE repos/:owner/:repo/actions/artifacts/{} 2>/dev/null || true
    echo -e "${GREEN}✓ Artifacts cleaned${NC}"
else
    echo -e "${YELLOW}GitHub CLI not installed. Install with: winget install GitHub.cli${NC}"
fi

# 3. Clean releases and tags
echo -e "${GREEN}Step 3: Releases and Tags Cleanup${NC}"
echo "Current tags:"
git tag -l

if confirm "Delete all tags?"; then
    # Delete local tags
    git tag -l | xargs -r git tag -d
    
    # Delete remote tags
    git ls-remote --tags origin | awk '{print $2}' | grep -v '{}' | sed 's/refs\/tags\///' | xargs -r -I {} git push origin --delete refs/tags/{} 2>/dev/null || true
    
    echo -e "${GREEN}✓ Tags cleaned${NC}"
fi

# 4. Clean repository secrets
echo -e "${GREEN}Step 4: Repository Secrets${NC}"
if command -v gh &> /dev/null; then
    echo "Current secrets:"
    gh secret list
    
    echo -e "${YELLOW}Note: Secrets cannot be deleted via CLI. Please review in GitHub UI.${NC}"
    echo "URL: https://github.com/$GITHUB_USER/$REPO_NAME/settings/secrets/actions"
fi

# 5. Clean git history (optional)
echo -e "${GREEN}Step 5: Git History${NC}"
if confirm "Do you want to create a fresh commit history (WARNING: This is destructive)?"; then
    # Create backup
    echo "Creating backup branch..."
    git checkout -b backup-$(date +%Y%m%d-%H%M%S)
    git checkout main
    
    # Create new orphan branch
    git checkout --orphan clean-main
    git add -A
    git commit -m "Initial commit - Fresh start for FoodXchange deployment"
    
    # Replace main branch
    git branch -D main
    git branch -m main
    
    echo -e "${GREEN}✓ Git history cleaned${NC}"
    echo -e "${YELLOW}You'll need to force push: git push -f origin main${NC}"
fi

# 6. Clean .git folder
echo -e "${GREEN}Step 6: Git Maintenance${NC}"
echo "Running git maintenance..."
git gc --prune=now --aggressive
git repack -a -d -f --depth=250 --window=250

# 7. Verify clean state
echo -e "${GREEN}Step 7: Verification${NC}"
echo "Repository status:"
git status
echo ""
echo "Repository size:"
du -sh .git
echo ""
echo "Tracked files:"
git ls-files | wc -l

echo -e "${GREEN}=== GitHub Cleanup Complete ===${NC}"
echo ""
echo "Next steps:"
echo "1. Review and update .gitignore"
echo "2. Ensure no sensitive data in tracked files"
echo "3. Update repository secrets in GitHub UI"
echo "4. Push clean repository to GitHub"