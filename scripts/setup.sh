#!/bin/bash

# AI Candidate Sourcing System - Setup Script

set -e

echo "=================================="
echo "AI Candidate Sourcing System Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.12"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.12+ required. Found: $python_version"
    exit 1
fi
echo "✓ Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p data logs
echo "✓ Directories created"

# Setup environment file
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your credentials:"
    echo "   - GROQ_API_KEY (get free key from groq.com)"
    echo "   - LINKEDIN_USERNAME"
    echo "   - LINKEDIN_PASSWORD"
else
    echo "✓ .env file already exists"
fi

# Check Chrome installation
echo ""
echo "Checking Chrome installation..."
if command -v google-chrome &> /dev/null || command -v chromium &> /dev/null; then
    echo "✓ Chrome/Chromium found"
else
    echo "⚠️  Chrome not found. Install Chrome for LinkedIn scraping:"
    echo "   macOS: brew install --cask google-chrome"
    echo "   Ubuntu: sudo apt-get install google-chrome-stable"
fi

# Run verification
echo ""
echo "Running verification..."
python scripts/verify_setup.py

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env with your credentials"
echo "2. Run: make run"
echo "3. Visit: http://localhost:8000/docs"
echo ""
