# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

An AI-powered system that detects scam messages, engages with scammers using adaptive personas, and extracts actionable intelligence for cybersecurity purposes.

## Live Demo

**Deployed URL:** `https://agentic-honey-pot-for-scam-detectio.vercel.app`

## Features

- **Scam Detection** - Rule-based + LLM-powered classification
- **Adaptive Persona** - Realistic character engagement to keep scammers talking
- **Intelligence Extraction** - Extracts UPI IDs, phone numbers, bank accounts, links
- **Multi-turn Conversations** - Maintains context across conversation sessions
- **Voice Detection** - AI-generated voice detection using audio analysis

## API Endpoints

### Text Honeypot Detection
```
POST /detect
```

**Headers:**
```
x-api-key: <your-api-key>
Content-Type: application/json
```

**Request:**
```json
{
  "sessionId": "unique-session-id",
  "message": "Your bank account is blocked. Call now!"
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "Oh dear, what happened to my account?"
}
```

### Voice Detection
```
POST /detect-voice
```

Analyzes audio files to detect AI-generated voices.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  FastAPI Application                 │
├─────────────────────────────────────────────────────┤
│   /detect          │        /detect-voice           │
├────────────────────┼────────────────────────────────┤
│   Orchestrator     │       Voice Detector           │
│   ├── Detector     │       └── Audio Analysis       │
│   ├── Persona      │                                │
│   ├── Extractor    │                                │
│   └── Memory       │                                │
└─────────────────────────────────────────────────────┘
```

## Local Development

### Prerequisites
- Python 3.9+
- Groq API Key (for LLM)

### Setup
```bash
# Clone repository
git clone https://github.com/Vaibhavsahkk/Agentic-Honey-Pot-for-Scam-Detection-Intelligence-Extraction.git
cd Agentic-Honey-Pot-for-Scam-Detection-Intelligence-Extraction

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your API keys

# Run server
uvicorn app.main:app --reload
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | API authentication key | - |
| `GROQ_API_KEY` | Groq LLM API key | - |
| `LLM_PROVIDER` | LLM provider (groq/openai/fallback) | fallback |
| `LLM_MODEL` | Model to use | llama3-70b-8192 |

## Project Structure

```
├── app/
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration management
│   ├── models.py         # Pydantic models
│   └── core/
│       ├── orchestrator.py   # Main coordinator
│       ├── detector.py       # Scam detection
│       ├── persona.py        # Persona management
│       ├── extractor.py      # Intelligence extraction
│       ├── memory.py         # Session memory
│       ├── voice_detector.py # Voice analysis
│       └── callback.py       # Callback handler
├── requirements.txt
├── vercel.json           # Vercel deployment config
└── README.md
```

## Tech Stack

- **Backend:** FastAPI, Python 3.9+
- **LLM:** Groq (Llama 3 70B)
- **Deployment:** Vercel (Serverless)
- **Audio Processing:** Librosa, NumPy

## License

MIT License

## Author

**Vaibhav Kumar**

---

Built for GUVI Hackathon 2026
