# 🕵️ Agentic Honey-Pot for Scam Detection

AI-powered system that detects scam messages, engages scammers autonomously, and extracts intelligence.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy example env file
copy .env.example .env

# Edit .env and set your API keys
```

### 3. Run the Server
```bash
python -m app.main
```

Server will start on `http://localhost:8000`

## 📡 API Usage

### Endpoint
```
POST http://localhost:8000/detect
```

### Headers
```
x-api-key: your-secret-api-key-here
Content-Type: application/json
```

### Request Body
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked. Verify immediately.",
    "timestamp": 1770005528731
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

### Response
```json
{
  "status": "success",
  "reply": "Why is my account being blocked? I don't understand."
}
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  API Layer (FastAPI)                 │
├─────────────────────────────────────────────────────┤
│                   Orchestrator                       │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐    │
│  │ Detector │→ │ Persona  │→ │  Extractor    │    │
│  └──────────┘  └──────────┘  └───────────────┘    │
│         ↓            ↓              ↓               │
│  ┌──────────────────────────────────────────────┐  │
│  │         Session Memory (In-Memory)           │  │
│  └──────────────────────────────────────────────┘  │
│                      ↓                              │
│         Final Callback to GUVI Endpoint             │
└─────────────────────────────────────────────────────┘
```

## 🎯 Core Features

✅ **Scam Detection** - Rule-based + LLM-powered classification  
✅ **Adaptive Persona** - Elderly Rajesh character with consistent responses  
✅ **Intelligence Extraction** - Extracts UPI IDs, links, phone numbers, bank accounts  
✅ **Multi-turn Conversations** - Maintains context across 15+ turns  
✅ **Final Callback** - Reports results to GUVI evaluation endpoint  

## 📁 Project Structure

```
HACKATHON/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic models
│   └── core/
│       ├── orchestrator.py  # Main coordinator
│       ├── detector.py      # Scam detection (TODO)
│       ├── persona.py       # Persona management (TODO)
│       ├── extractor.py     # Intelligence extraction (TODO)
│       ├── memory.py        # Session memory (TODO)
│       └── callback.py      # GUVI callback (TODO)
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 Configuration

Edit `.env` file:

```bash
# API Settings
API_KEY=your-secret-api-key-here
PORT=8000

# Choose LLM Provider
LLM_PROVIDER=groq  # Options: openai, groq, fallback
GROQ_API_KEY=your-groq-key-here
# OR
OPENAI_API_KEY=sk-your-key-here

# System Settings
MAX_CONVERSATION_TURNS=15
MIN_INTELLIGENCE_THRESHOLD=2
DEBUG_MODE=true
```

## 🧪 Testing

```bash
# Health check
curl http://localhost:8000/health

# Test detection endpoint
curl -X POST http://localhost:8000/detect \
  -H "x-api-key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

## 📊 Status

**Current Progress:**
- ✅ Project structure
- ✅ FastAPI setup
- ✅ API models
- ✅ Orchestrator framework
- ⏳ Detector (next)
- ⏳ Persona system (next)
- ⏳ Extractor (next)
- ⏳ Memory (next)
- ⏳ Callback integration (next)

## 🎓 Built For

GUVI Hackathon - Problem Statement 2: Agentic Honey-Pot

---

**Next Steps:** Implement core modules (detector, persona, extractor)
