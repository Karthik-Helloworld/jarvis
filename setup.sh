#!/bin/bash
# JARVIS Setup Script — macOS
# Run once: bash setup.sh

set -e

echo ""
echo "⚡ JARVIS Setup — macOS"
echo "========================"
echo ""

if ! command -v python3 &>/dev/null; then
  echo "❌ Python 3 not found. Install from https://python.org and re-run."
  exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(sys.version_info.minor)")
if [ "$PYTHON_VERSION" -lt 10 ]; then
  echo "❌ Python 3.10+ required. You have 3.$PYTHON_VERSION."
  exit 1
fi
echo "✅ Python 3.$PYTHON_VERSION found."

if ! command -v brew &>/dev/null; then
  echo "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
echo "✅ Homebrew ready."

echo "Installing ffmpeg (needed by Whisper)..."
brew install ffmpeg 2>/dev/null || echo "ffmpeg already installed."
echo "✅ ffmpeg ready."

echo ""
echo "Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing Python packages..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo ""
echo "✅ All packages installed."
echo ""

if [ ! -f .env ]; then
  cp .env.example .env
  echo "📄 Created .env file — open it and paste your API keys:"
  echo "   ANTHROPIC_API_KEY  → https://console.anthropic.com"
  echo "   ELEVENLABS_API_KEY → https://elevenlabs.io"
  echo ""
  echo "Then run:  source .venv/bin/activate && python jarvis.py"
else
  echo "✅ .env already exists."
  echo ""
  echo "To start JARVIS:"
  echo "  source .venv/bin/activate"
  echo "  python jarvis.py"
fi

echo ""
echo "🤖 JARVIS is ready to deploy."
