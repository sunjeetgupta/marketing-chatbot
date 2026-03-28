#!/bin/bash
set -e

echo "🚀 Setting up Marketing Campaign AI Chatbot"
echo "============================================"

# ─── Backend setup ──────────────────────────────
echo ""
echo "📦 Setting up Python backend..."
cd backend

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "✅ Created backend/.env — please add your ANTHROPIC_API_KEY"
fi

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend dependencies installed"
deactivate

# ─── Frontend setup ─────────────────────────────
echo ""
echo "📦 Setting up React frontend..."
cd ../frontend

npm install

echo "✅ Frontend dependencies installed"

# ─── Done ───────────────────────────────────────
echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo ""
echo "  Terminal 1 (backend):"
echo "    cd backend"
echo "    source venv/bin/activate"
echo "    uvicorn main:app --reload --port 8000"
echo ""
echo "  Terminal 2 (frontend):"
echo "    cd frontend"
echo "    npm run dev"
echo ""
echo "Then open: http://localhost:5173"
echo ""
echo "📋 Required:"
echo "  - ANTHROPIC_API_KEY in backend/.env"
echo ""
echo "📋 Optional (for open-source LLM):"
echo "  - Install Ollama: https://ollama.ai"
echo "  - Run: ollama pull llama3.2"
echo "  - The audience agent uses Ollama if available, otherwise falls back to Claude"
