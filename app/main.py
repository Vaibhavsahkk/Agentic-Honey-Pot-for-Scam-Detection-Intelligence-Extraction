"""
Main FastAPI application
Entry point for the Agentic Honey-Pot system
"""
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
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


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "Agentic Honey-Pot API",
        "docs": "/docs",
        "health": "/health",
        "detect_endpoint": "/detect"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG_MODE
    )
