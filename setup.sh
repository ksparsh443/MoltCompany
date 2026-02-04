#!/bin/bash
# Quick Start Script for AI Company

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        🏢 AI COMPANY - QUICK START SETUP                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies (this may take a few minutes)..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp .env.template .env
    echo "⚠️  IMPORTANT: Edit .env and add your Hugging Face API key!"
    echo "   Get it from: https://huggingface.co/settings/tokens"
fi

# Create directories
echo ""
echo "📁 Creating workspace directories..."
mkdir -p data/memory
mkdir -p agent_workspace/pending_approval
mkdir -p agent_workspace/approved

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    ✅ SETUP COMPLETE!                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env and add your Hugging Face API key:"
echo "   nano .env"
echo "   (Add: HUGGINGFACE_API_KEY=hf_your_token_here)"
echo ""
echo "2. Test it:"
echo "   python test_local.py"
echo ""
echo "3. Or start API server:"
echo "   python api_server.py"
echo ""
echo "Get your FREE Hugging Face token:"
echo "→ https://huggingface.co/settings/tokens"
echo ""
