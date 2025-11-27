#!/bin/bash

# Git Setup Script for AI Candidate Sourcing System

echo "=================================="
echo "Git Repository Setup"
echo "=================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    echo "✓ Git initialized"
else
    echo "✓ Git already initialized"
fi

# Check git user config
echo ""
echo "Git Configuration:"
echo "  User: $(git config user.name)"
echo "  Email: $(git config user.email)"

# Add all files
echo ""
echo "Staging files..."
git add .
echo "✓ Files staged"

# Show status
echo ""
echo "Git Status:"
git status --short

# Create initial commit
echo ""
read -p "Create initial commit? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit -m "feat: initial production-ready release

- Multi-portal candidate scraping (LinkedIn, StackOverflow, Indeed, Glassdoor)
- AI-powered matching with embeddings
- LLM reasoning with Groq
- Multi-factor ranking system
- REST API with FastAPI
- Docker support
- Comprehensive documentation
- Production deployment configurations"
    echo "✓ Initial commit created"
fi

# Instructions for GitHub
echo ""
echo "=================================="
echo "Next Steps:"
echo "=================================="
echo ""
echo "1. Create a new repository on GitHub:"
echo "   https://github.com/new"
echo ""
echo "2. Add the remote repository:"
echo "   git remote add origin https://github.com/sanyamk23/your-repo-name.git"
echo ""
echo "3. Push to GitHub:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "Or use the GitHub CLI:"
echo "   gh repo create ai-candidate-sourcing --public --source=. --remote=origin"
echo "   git push -u origin main"
echo ""
