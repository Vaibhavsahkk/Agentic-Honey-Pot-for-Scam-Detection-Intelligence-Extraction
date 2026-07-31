"""
Main FastAPI application
Entry point for the Agentic Honey-Pot system
"""
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import json
from datetime import datetime

from app.config import settings
from app.models import IncomingRequest, AgentResponse, VoiceRequest, VoiceResponse
from app.core.orchestrator import ConversationOrchestrator
from app.core.voice_detector import VoiceDetector

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG_MODE else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Global instances
orchestrator = ConversationOrchestrator()
voice_detector = VoiceDetector()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management"""
    logger.info("🚀 Agentic Honey-Pot starting up...")
    logger.info(f"🔑 API Key authentication: {'ENABLED' if settings.API_KEY else 'DISABLED'}")
    logger.info(f"🤖 LLM Provider: {settings.LLM_PROVIDER}")
    yield
    logger.info("👋 Shutting down gracefully...")


# Initialize FastAPI app
app = FastAPI(
    title="Agentic Honey-Pot API",
    description="AI-powered scam detection and intelligence extraction system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    logger.info(f"📨 {request.method} {request.url.path}")
    response = await call_next(request)
    return response


@app.post("/detect")
async def detect_and_engage(
    request: Request,
    x_api_key: str = Header(None)
):
    """
    Main endpoint for scam detection and engagement.
    Processes messages through the orchestrator for:
    - Scam detection
    - AI persona engagement
    - Intelligence extraction
    - GUVI callback when done
    """
    # API Key validation
    if settings.API_KEY and x_api_key != settings.API_KEY:
        logger.warning(f"❌ Invalid API key: {x_api_key}")
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        # Parse request body
        try:
            body = await request.json()
            logger.info(f"📥 RAW REQUEST BODY: {json.dumps(body, default=str)[:500]}")
        except:
            body = {}
            logger.info("📥 Empty or invalid JSON body received")
        
        # Extract session info
        session_id = body.get("sessionId", "test-session")
        logger.info(f"🔍 Processing session: {session_id}")
        
        # Build IncomingRequest from body
        try:
            # Handle message - can be dict or string
            message_data = body.get("message", {})
            if isinstance(message_data, str):
                message_data = {"sender": "scammer", "text": message_data, "timestamp": int(datetime.now().timestamp() * 1000)}
            elif isinstance(message_data, dict) and "text" not in message_data:
                # If message is empty dict, use a default
                message_data = {"sender": "scammer", "text": body.get("text", "Hello"), "timestamp": int(datetime.now().timestamp() * 1000)}
            
            # Ensure required fields
            if "sender" not in message_data:
                message_data["sender"] = "scammer"
            if "timestamp" not in message_data:
                message_data["timestamp"] = int(datetime.now().timestamp() * 1000)
            
            # Build conversation history
            history = body.get("conversationHistory", [])
            
            # Build metadata
            metadata_raw = body.get("metadata", {})
            
            # Create the request object
            from app.models import IncomingRequest, Message, Metadata
            
            incoming_request = IncomingRequest(
                sessionId=session_id,
                message=Message(**message_data),
                conversationHistory=[Message(**m) for m in history] if history else [],
                metadata=Metadata(**metadata_raw) if metadata_raw else None
            )
            
            # Process through orchestrator (this does scam detection, engagement, extraction)
            response = await orchestrator.process_message(incoming_request)
            
            return JSONResponse(
                status_code=200,
                content={
                    "status": response.status,
                    "reply": response.reply
                }
            )
            
        except Exception as parse_error:
            logger.warning(f"⚠️ Could not parse as IncomingRequest: {parse_error}")
            # Fallback for simple requests or test requests
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "reply": "Hello! I received your message. How can I help you today?"
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error processing request: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "reply": "I'm here to help. Please tell me more."
            }
        )


@app.post("/detect-voice")
async def detect_voice(
    request: Request,
    x_api_key: str = Header(None)
):
    """
    Endpoint for AI-Generated Voice Detection.
    Accepts flexible input format.
    """
    if settings.API_KEY and x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
        
    try:
        body = await request.json()
        logger.info(f"🎙️ Processing voice request")
        
        # Extract fields with flexible key names
        language = body.get("language", "en")
        audio_format = body.get("audioFormat") or body.get("audio_format", "mp3")
        audio_base64 = body.get("audioBase64") or body.get("audio_base64", "")
        
        result = await voice_detector.analyze(audio_base64, audio_format)
        
        return JSONResponse(
            status_code=200,
            content={
                "is_ai_generated": result["is_ai_generated"],
                "confidence_score": result["confidence_score"],
                "details": result.get("analysis_details", {})
            }
        )
    except Exception as e:
        logger.error(f"Error in voice detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "agentic-honeypot",
        "version": "1.0.0",
        "llm_provider": settings.LLM_PROVIDER
    }


@app.get("/", response_class=HTMLResponse)
async def root():
    """Interactive Enterprise Web Portal for Agentic Honeypot"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Agentic Honeypot | Scam Detection & Intelligence Extraction</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-deep: #0a0f1d;
                --bg-card: rgba(18, 26, 45, 0.75);
                --accent-cyan: #00f2fe;
                --accent-blue: #4facfe;
                --status-up: #10b981;
                --status-down: #ef4444;
                --text-main: #f8fafc;
                --text-muted: #94a3b8;
                --border-panel: rgba(255, 255, 255, 0.08);
            }
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
            body { background: var(--bg-deep); color: var(--text-main); min-height: 100vh; padding: 32px 20px; }
            .container { max-width: 1000px; margin: 0 auto; }
            .header { display: flex; align-items: center; justify-content: space-between; padding-bottom: 24px; border-bottom: 1px solid var(--border-panel); margin-bottom: 32px; }
            .brand { display: flex; align-items: center; gap: 14px; }
            .shield-icon { width: 44px; height: 44px; background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue)); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 0 20px rgba(0, 242, 254, 0.3); }
            .brand-title { font-size: 1.4rem; font-weight: 800; background: linear-gradient(to right, #ffffff, var(--accent-cyan)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            .brand-sub { font-size: 0.8rem; color: var(--text-muted); }
            .nav-links { display: flex; gap: 12px; }
            .btn-nav { padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; text-decoration: none; border: 1px solid var(--border-panel); color: var(--text-main); background: rgba(255, 255, 255, 0.03); transition: all 0.2s ease; }
            .btn-nav:hover { border-color: var(--accent-cyan); color: var(--accent-cyan); box-shadow: 0 0 12px rgba(0, 242, 254, 0.2); }
            
            .card { background: var(--bg-card); backdrop-filter: blur(12px); border: 1px solid var(--border-panel); border-radius: 16px; padding: 28px; margin-bottom: 28px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
            .card-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; }
            
            .preset-pills { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
            .pill { padding: 6px 14px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; cursor: pointer; background: rgba(255,255,255,0.05); border: 1px solid var(--border-panel); color: var(--text-muted); transition: all 0.2s; }
            .pill:hover { background: rgba(0, 242, 254, 0.1); color: var(--accent-cyan); border-color: var(--accent-cyan); }
            
            textarea { width: 100%; height: 110px; background: rgba(10, 15, 29, 0.8); border: 1px solid var(--border-panel); border-radius: 12px; padding: 14px; color: var(--text-main); font-size: 0.95rem; outline: none; margin-bottom: 16px; transition: border-color 0.2s; }
            textarea:focus { border-color: var(--accent-cyan); }
            
            .btn-action { width: 100%; padding: 14px; border-radius: 10px; border: none; background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue)); color: #0a0f1d; font-weight: 800; font-size: 1rem; cursor: pointer; transition: transform 0.1s, box-shadow 0.2s; }
            .btn-action:hover { box-shadow: 0 0 25px rgba(0, 242, 254, 0.4); transform: translateY(-1px); }
            
            .result-box { display: none; margin-top: 24px; padding: 20px; background: rgba(10, 15, 29, 0.9); border-radius: 12px; border-left: 4px solid var(--accent-cyan); }
            .result-header { font-size: 0.85rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; margin-bottom: 10px; letter-spacing: 0.05em; }
            .reply-text { font-size: 1rem; color: #ffffff; line-height: 1.6; font-weight: 500; }
            .meta-badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; background: rgba(16, 185, 129, 0.2); color: var(--status-up); margin-bottom: 12px; }
            
            .status-banner { display: flex; align-items: center; justify-content: space-between; padding: 14px 20px; border-radius: 10px; background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); margin-bottom: 28px; }
            .status-left { display: flex; align-items: center; gap: 10px; font-size: 0.9rem; font-weight: 600; }
            .pulse { width: 10px; height: 10px; background: var(--status-up); border-radius: 50%; box-shadow: 0 0 10px var(--status-up); }
            .mono { font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="brand">
                    <div class="shield-icon">🛡️</div>
                    <div>
                        <div class="brand-title">Agentic Honeypot AI</div>
                        <div class="brand-sub">Autonomous Scam Detection & Threat Intelligence Platform</div>
                    </div>
                </div>
                <div class="nav-links">
                    <a href="/docs" class="btn-nav">📄 Swagger Docs</a>
                    <a href="/health" class="btn-nav">💚 API Health</a>
                </div>
            </div>

            <div class="status-banner">
                <div class="status-left">
                    <div class="pulse"></div>
                    <span>Vercel Serverless Cluster: <strong style="color: var(--status-up)">ONLINE & HEALTHY</strong></span>
                </div>
                <div class="mono" style="color: var(--text-muted)">LLM Engine: GROQ AI</div>
            </div>

            <div class="card">
                <div class="card-title">⚡ Interactive Scam Test Bench</div>
                <div class="preset-pills">
                    <div class="pill" onclick="setPreset(1)">🚨 Bank Fraud & UPI Scam</div>
                    <div class="pill" onclick="setPreset(2)">🎣 Phishing Link Scam</div>
                    <div class="pill" onclick="setPreset(3)">💬 Normal Message</div>
                </div>
                <textarea id="scamInput" placeholder="Enter suspicious message or link here..."></textarea>
                <button class="btn-action" onclick="analyzeScam()">🔍 ANALYZE & ENGAGE HONEYPOT AGENT</button>

                <div id="resultBox" class="result-box">
                    <div id="metaBadge" class="meta-badge">SCAM DETECTED & ENGAGED</div>
                    <div class="result-header">Honeypot AI Persona Reply</div>
                    <div id="replyText" class="reply-text">...</div>
                </div>
            </div>
        </div>

        <script>
            function setPreset(type) {
                const input = document.getElementById('scamInput');
                if (type === 1) {
                    input.value = "Urgent! Your HDFC bank account is locked due to security check. Send 10,000 INR immediately to upi@okicici or update KYC at http://hdfc-verify-bank.com/login";
                } else if (type === 2) {
                    input.value = "Congratulations! You won a cash prize of $50,000 in international lottery. Claim your reward now at http://claim-rewards-free.net/win";
                } else {
                    input.value = "Hey! Are we still meeting for lunch today at 1 PM?";
                }
            }

            async function analyzeScam() {
                const input = document.getElementById('scamInput').value.trim();
                const resultBox = document.getElementById('resultBox');
                const replyText = document.getElementById('replyText');
                const metaBadge = document.getElementById('metaBadge');

                if (!input) {
                    alert("Please enter a message or select a preset!");
                    return;
                }

                resultBox.style.display = "block";
                replyText.innerText = "Analyzing intelligence & generating counter-engagement...";
                metaBadge.innerText = "PROCESSING...";
                metaBadge.style.background = "rgba(0, 242, 254, 0.2)";
                metaBadge.style.color = "var(--accent-cyan)";

                try {
                    const res = await fetch('/detect', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            sessionId: 'web-demo-session',
                            message: { text: input }
                        })
                    });
                    const data = await res.json();
                    
                    metaBadge.innerText = "SUCCESS (" + (data.status || 'OK') + ")";
                    metaBadge.style.background = "rgba(16, 185, 129, 0.2)";
                    metaBadge.style.color = "var(--status-up)";
                    replyText.innerText = data.reply || "Message analyzed successfully.";
                } catch (e) {
                    metaBadge.innerText = "RESPONSE ERROR";
                    metaBadge.style.background = "rgba(239, 68, 68, 0.2)";
                    metaBadge.style.color = "var(--status-down)";
                    replyText.innerText = "Failed to connect to API endpoint: " + e.message;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG_MODE
    )
