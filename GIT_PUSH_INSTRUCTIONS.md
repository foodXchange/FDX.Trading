# Git Push Instructions - AI Search Feature

## Issue
GitHub is blocking pushes due to API keys in the repository history. The repository has push protection enabled that detects secrets.

## Your Options

### Option 1: Use GitHub Web Interface
1. Go to the URLs provided in the error messages to allow the secrets
2. Or manually create the files through GitHub web interface

### Option 2: Clean Repository History
1. Remove all API keys from `.env` files
2. Use `git filter-branch` or BFG Repo-Cleaner to remove secrets from history
3. Force push (requires admin rights)

### Option 3: Create Pull Request
1. Fork the repository
2. Add the changes to your fork
3. Create a pull request

## Files to Add Manually

The AI search integration includes these files:
- `app.py` (updated with AI search routes)
- `ai_search_system.py`
- `email_response_analyzer.py`
- `setup_search_system_tables.py`
- `templates/suppliers_simple.html`
- `templates/suppliers_ai.html`
- `README_AI_SEARCH.md`

## Local Branch
Your changes are saved in the local branch: `feature/ai-search-integration`

To see the changes:
```bash
git checkout feature/ai-search-integration
git log --oneline
```

## Safe Alternative
Consider creating a new repository without the secret history, or contact the repository admin to help with the push protection.