# GitHub Setup Guide

## Current Git Configuration

**User:** sanyamk23  
**Email:** sanyamkumat2305@gmail.com  
**Status:** Local repository, no remote configured

## Option 1: Using GitHub Web Interface (Recommended)

### Step 1: Create Repository on GitHub

1. Go to [https://github.com/new](https://github.com/new)
2. Fill in the details:
   - **Repository name**: `ai-candidate-sourcing` (or your preferred name)
   - **Description**: "AI-powered candidate sourcing system with multi-portal scraping and intelligent ranking"
   - **Visibility**: Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
3. Click "Create repository"

### Step 2: Connect Local Repository

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add remote
git remote add origin https://github.com/sanyamk23/ai-candidate-sourcing.git

# Stage all files
git add .

# Create initial commit
git commit -m "feat: initial production-ready release

- Multi-portal candidate scraping (LinkedIn, StackOverflow, Indeed, Glassdoor)
- AI-powered matching with embeddings
- LLM reasoning with Groq
- Multi-factor ranking system
- REST API with FastAPI
- Docker support
- Comprehensive documentation
- Production deployment configurations"

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Verify

Visit your repository: `https://github.com/sanyamk23/ai-candidate-sourcing`

---

## Option 2: Using GitHub CLI (Faster)

If you have GitHub CLI installed:

```bash
# Login to GitHub (if not already)
gh auth login

# Create repository and push
gh repo create ai-candidate-sourcing --public --source=. --remote=origin --description "AI-powered candidate sourcing system"

# Stage and commit
git add .
git commit -m "feat: initial production-ready release"

# Push
git push -u origin main
```

---

## Option 3: Manual Setup (Step by Step)

### 1. Initialize Git (already done)

```bash
git init
```

### 2. Stage Files

```bash
# Stage all files
git add .

# Or stage specific files
git add src/ tests/ docs/
git add README.md requirements.txt Dockerfile
git add Makefile docker-compose.yml
```

### 3. Create Initial Commit

```bash
git commit -m "feat: initial production-ready release

- Multi-portal candidate scraping
- AI-powered matching
- REST API with FastAPI
- Docker support
- Production configurations"
```

### 4. Create GitHub Repository

Go to GitHub and create a new repository (see Option 1, Step 1)

### 5. Add Remote and Push

```bash
# Add remote (replace with your actual repo URL)
git remote add origin https://github.com/sanyamk23/your-repo-name.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Recommended Repository Settings

After pushing to GitHub:

### 1. Add Repository Description

- Go to repository settings
- Add description: "AI-powered candidate sourcing system with multi-portal scraping and intelligent ranking"
- Add topics: `ai`, `recruitment`, `scraping`, `fastapi`, `python`, `machine-learning`

### 2. Enable GitHub Pages (Optional)

- Settings → Pages
- Source: Deploy from branch
- Branch: main, /docs folder
- Your docs will be available at: `https://sanyamk23.github.io/ai-candidate-sourcing/`

### 3. Add Branch Protection (Recommended)

- Settings → Branches
- Add rule for `main` branch
- Enable:
  - Require pull request reviews
  - Require status checks to pass
  - Require branches to be up to date

### 4. Add Secrets (for CI/CD)

- Settings → Secrets and variables → Actions
- Add secrets:
  - `GROQ_API_KEY`
  - `LINKEDIN_USERNAME`
  - `LINKEDIN_PASSWORD`

### 5. Enable Issues and Discussions

- Settings → Features
- Enable Issues
- Enable Discussions (optional)

---

## .gitignore Verification

Make sure these are in `.gitignore`:

```
# Sensitive files
.env
.env.local
.env.production

# Data
data/*.db
logs/*.log

# Python
__pycache__/
*.pyc
venv/
```

---

## Future Commits

### Daily Workflow

```bash
# Check status
git status

# Stage changes
git add .

# Commit with meaningful message
git commit -m "fix: update LinkedIn scraper selectors"

# Push to GitHub
git push
```

### Commit Message Format

Follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `chore:` Maintenance

Examples:
```bash
git commit -m "feat: add Indeed scraper support"
git commit -m "fix: resolve LinkedIn login timeout"
git commit -m "docs: update API documentation"
git commit -m "test: add matcher unit tests"
```

---

## Branching Strategy

### For Features

```bash
# Create feature branch
git checkout -b feature/new-scraper

# Make changes and commit
git add .
git commit -m "feat: add new scraper"

# Push feature branch
git push -u origin feature/new-scraper

# Create Pull Request on GitHub
# After review and merge, delete branch
git checkout main
git pull
git branch -d feature/new-scraper
```

### For Bug Fixes

```bash
# Create fix branch
git checkout -b fix/linkedin-timeout

# Make changes and commit
git add .
git commit -m "fix: increase LinkedIn timeout"

# Push and create PR
git push -u origin fix/linkedin-timeout
```

---

## Useful Git Commands

```bash
# View commit history
git log --oneline --graph

# View changes
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard local changes
git checkout -- filename

# Update from remote
git pull

# View remote info
git remote -v

# Create and switch to new branch
git checkout -b branch-name

# Switch branches
git checkout main

# Delete branch
git branch -d branch-name
```

---

## GitHub Actions (Optional CI/CD)

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: make test
      - run: make lint
```

---

## Troubleshooting

### Authentication Issues

If you get authentication errors:

```bash
# Use personal access token
# Generate at: https://github.com/settings/tokens
# Use token as password when prompted

# Or use SSH
git remote set-url origin git@github.com:sanyamk23/ai-candidate-sourcing.git
```

### Large Files

If you have large files:

```bash
# Use Git LFS
git lfs install
git lfs track "*.db"
git add .gitattributes
```

### Accidentally Committed Secrets

```bash
# Remove from history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
```

Then rotate all exposed secrets immediately!

---

## Quick Start Script

Run the setup script:

```bash
./scripts/git_setup.sh
```

This will:
1. Initialize git (if needed)
2. Stage all files
3. Create initial commit
4. Show next steps

---

## Need Help?

- GitHub Docs: https://docs.github.com
- Git Docs: https://git-scm.com/doc
- GitHub CLI: https://cli.github.com

---

**Ready to push?** Follow Option 1 above to get started! 🚀
