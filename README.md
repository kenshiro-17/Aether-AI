# Aether

A privacy-focused, local-first AI assistant that runs entirely on your own hardware. No cloud dependencies, no data leaving your machine.

## What is this?

Aether is a personal AI system I built because I wanted an AI assistant that:
- Runs completely offline on my own GPU
- Keeps all my data local
- Can search the web, analyze images, and execute code when needed
- Remembers context across sessions using a vector database

## Architecture

The system consists of several components:

- **Backend** - FastAPI server handling chat, memory, and tool execution
- **Frontend** - React + Electron desktop app
- **LLM Server** - Llama.cpp serving local models (Llama 3, Mistral, etc.)
- **Memory** - Qdrant vector DB for long-term knowledge storage
- **Mobile** - React Native companion app (WIP)

## Requirements

- Windows 10/11 (x64)
- NVIDIA GPU with 8GB+ VRAM (or AMD with Vulkan)
- Python 3.10+
- Node.js 18+
- GGUF model files in `models/` directory

## Setup

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```

### Models

Download your preferred GGUF models and place them in the `models/` folder. I typically use:
- Llama 3.2 3B for fast responses
- Llama 3.3 8B for complex reasoning
- LLaVA Phi-3 for image analysis

## Running

Just run `start_system.bat` - it handles starting all the services.

To stop, close the terminal window.

## Project Structure

```
backend/           # FastAPI server
  cortex/          # AI capabilities (search, vision, etc.)
  routers/         # API endpoints
frontend/          # React + Electron UI
  src/components/  # UI components
  electron/        # Desktop app wrapper
mobile/            # React Native app
models/            # GGUF model files (not tracked)
scripts/           # Utility scripts
```

## Features

- Real-time streaming responses
- Web search with automatic source verification
- Image analysis and OCR
- Secure Python code execution (sandboxed)
- Long-term memory via RAG
- Multi-model support (swap models on the fly)

## Security

- All LLM inference runs locally
- Code execution is sandboxed with AST-level blocking of dangerous imports
- Electron renderer is sandboxed (no Node.js access)
- Strict CSP headers on frontend
- PBKDF2-SHA256 password hashing

## License

MIT
