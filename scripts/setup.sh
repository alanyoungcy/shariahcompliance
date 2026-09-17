#!/bin/bash

# Shariah Compliance Copilot - Setup Script

set -e

echo "🚀 Setting up Shariah Compliance Copilot..."

# Check Python version
echo "📌 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p data/uploads
mkdir -p data/reports
mkdir -p data/generated_contracts/compliant
mkdir -p data/generated_contracts/non_compliant
mkdir -p data/aaoifi_standards
mkdir -p data/fatwa_database
mkdir -p logs

# Copy environment template if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "🔐 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your provider credentials"
else
    echo "✅ .env file already exists"
fi

# Generate sample contracts
echo "📄 Generating sample contracts..."
if [ -f "src/generators/contract_generator.py" ]; then
    python src/generators/contract_generator.py
    echo "✅ Generated sample contracts"
else
    echo "⚠️  Contract generator not found yet - will be available after implementation"
fi

# Check Node.js for frontend (optional)
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo "✅ Node.js $node_version found"
    
    if [ -d "src/frontend" ] && [ -f "src/frontend/package.json" ]; then
        echo "📦 Installing frontend dependencies..."
        cd src/frontend
        npm install
        cd ../..
        echo "✅ Frontend dependencies installed"
    else
        echo "ℹ️  Frontend not implemented yet"
    fi
else
    echo "⚠️  Node.js not found - frontend will not be available"
fi

# Summary
echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your provider credentials"
echo "2. Activate venv: source venv/bin/activate"
echo "3. Run backend: uvicorn src.backend.main:app --reload"
echo "4. Run frontend (if available): cd src/frontend && npm run dev"
echo ""
echo "📖 See README.md for full documentation"
