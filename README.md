<div align="center">

<img src="frontend/public/favicon.svg" alt="CodeReview AI Logo" width="80" height="80"/>

# CodeReview AI

**AI-powered code review that runs 100% on your machine.**  
No cloud. No API keys. No data leaves your servers.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal?style=flat-square&logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)
![Ollama](https://img.shields.io/badge/Ollama-llama3.2:3b-orange?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)

</div>

---

## What It Does

Paste a raw git diff, a PR description, or any block of code — CodeReview AI returns a structured review powered by the **Ollama `llama3.2:3b`** model running locally.

| Section | Description |
|---|---|
| 📋 **Change Summary** | Plain-English explanation of what the code does |
| 🚩 **Risk Flags** | Bugs, security issues, and edge cases with **Low / Medium / High** severity |
| 💡 **Suggestions** | Line-level improvement recommendations |
| ⭐ **Overall Rating** | *Looks Good*, *Needs Minor Changes*, or *Needs Major Rework* |

---

## Quick Start (Docker)

The easiest way to run this. No Python or Node setup required.

```bash
git clone https://github.com/YOUR_USERNAME/codereview-ai.git
cd codereview-ai
docker compose up -d
```

> **Note:** On the first run, the Ollama container will automatically pull the `llama3.2:3b` model (~2GB). This takes a few minutes depending on your internet speed.

**Then open:** `http://localhost`

---

## Manual Setup (Development)

**1. Backend**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**2. Frontend**
```bash
cd frontend
npm install
npm run dev
```

**3. Ollama**
```bash
# Install from https://ollama.ai
ollama pull llama3.2:3b
```

Then open: `http://localhost:5173`

---

## Tech Stack

| Layer | Technology |
|---|---|
| **AI Engine** | [Ollama](https://ollama.ai) + `llama3.2:3b` (local) |
| **Backend** | FastAPI + SQLAlchemy + SQLite |
| **Frontend** | React 18 + Vite + Vanilla CSS |
| **Deployment** | Docker Compose |

---

## Project Structure

```
codereview-ai/
├── backend/
│   ├── main.py            # FastAPI app & endpoints
│   ├── models.py          # SQLAlchemy & Pydantic models
│   ├── database.py        # DB engine & session
│   ├── ollama_service.py  # Ollama API integration
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx        # Main React component
│   │   └── index.css      # Premium dark-mode styles
│   ├── public/
│   │   └── favicon.svg    # App logo
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Privacy

All analysis is performed **locally**. Your code is sent to `localhost:11434` (your own Ollama instance) and never transmitted externally.

---

<div align="center">
  <sub>Built with ❤️ — private, fast, and free.</sub>
</div>
