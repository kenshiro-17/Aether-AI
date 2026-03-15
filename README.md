# Aether-AI

Local-first AI assistant built to run on your own hardware with private inference, long-term memory, tool use, and desktop-native interaction.

Aether is designed for people who want assistant capabilities without handing their documents, prompts, or workflows to a cloud service by default. The stack combines local LLM serving, a FastAPI backend, a React and Electron desktop UI, and Qdrant-backed memory.

## Core Capabilities

- Local-first chat and task assistance
- Long-term memory with Qdrant vector storage
- Multi-model support for different latency and quality targets
- Web search and research tooling
- Vision and OCR support through multimodal models
- Sandboxed Python execution with AST-based restrictions
- Electron desktop UI and in-progress mobile client
- Model-management helpers for GGUF-based local inference

## Architecture

```text
Frontend (React + Electron)
  -> FastAPI backend
  -> local model runtime (llama.cpp / OpenAI-compatible local endpoint)
  -> Qdrant memory layer
  -> tool services for search, vision, and controlled execution
```

Primary areas:

- `backend/`: API, auth, memory, model management, tool orchestration
- `frontend/`: Vite + React desktop interface with Electron wrapper
- `mobile/aether-mobile/`: React Native companion app
- `infra/docker-compose.yml`: local service composition
- `scripts/`: model update and runtime helper scripts

## Tech Stack

- FastAPI
- React + Electron
- React Native (mobile WIP)
- Qdrant
- `llama.cpp` / GGUF local models
- Python tool layer for memory, research, and execution

## Hardware and Runtime Requirements

- Windows 10 or 11 recommended
- Python 3.10+
- Node.js 18+
- GPU recommended for good local performance
- GGUF model files available locally

Model selection in the repo suggests support for options such as:

- Llama 3.2 3B
- Llama 3.3 8B
- Llama 4 Scout 17B
- DeepSeek R1 Distill Llama 8B
- LLaVA Phi-3 for image analysis

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/kenshiro-17/Aether-AI.git
cd Aether-AI
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend setup

```bash
cd ../frontend
npm install
```

### 4. Optional mobile setup

```bash
cd ../mobile/aether-mobile
npm install
```

### 5. Prepare models

Place GGUF model files in the local models directory expected by the project. The repo includes model-management scripts and references to supported files in `backend/model_manager.py`.

### 6. Run the system

On Windows, the easiest path is:

```bash
start_system.bat
```

This is the intended orchestration entrypoint for the local stack.

## Alternative Service Paths

### Backend directly

```bash
cd backend
venv\Scripts\activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend desktop development

```bash
cd frontend
npm run electron:dev
```

### Docker services

The repo includes `infra/docker-compose.yml`, which provisions backend and Qdrant together.

## What Makes It Local-First

- Inference is designed to run against locally available models
- Qdrant can run locally through file-backed storage or service mode
- The Electron renderer is sandboxed
- Sensitive user context does not need to leave the machine
- Tool execution is constrained rather than fully open-ended

## Security Notes

Controls visible in the repo include:

- AST-level blocking of dangerous Python imports
- Electron preload isolation and sandboxing
- PBKDF2-SHA256 password hashing
- CSP and hardened frontend behavior
- Memory cleanup and explicit Qdrant resource handling

## Useful Repo Scripts

- `start_system.bat`: primary startup flow
- `scripts/update_llama.py`: local model runtime update helper
- `scripts/check_llm_status.py`: local model server status check
- `verify_backend_startup.py`: backend verification helper

## Verification

Suggested local checks:

```bash
python verify_backend_startup.py
python test_register.py
```

If you are working on the memory layer, inspect `tests/test_memory.py` as well.

## Project Layout

```text
backend/
frontend/
mobile/
infra/
scripts/
tests/
```

## Notes for Contributors

This repo is closer to a personal AI workstation than a single API service. If you change one area, check the assumptions in the others:

- backend auth and tool execution
- frontend desktop security model
- local model path configuration
- Qdrant memory persistence

## License

MIT
