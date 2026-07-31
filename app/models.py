"""
Pydantic models for API request/response validation
Matches GUVI hackathon specifications exactly
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class Message(BaseModel):
    """Single message in conversation"""
    sender: Literal["scammer", "user"]
    text: str
    timestamp: int  # Epoch time in milliseconds


class Metadata(BaseModel):
    """Optional metadata about the message"""
    channel: Optional[str] = "SMS"
    language: Optional[str] = "English"
    locale: Optional[str] = "IN"


class IncomingRequest(BaseModel):
    """Request format from GUVI platform"""
    sessionId: str
    message: Message
    conversationHistory: List[Message] = Field(default_factory=list)
    metadata: Optional[Metadata] = None


class VoiceRequest(BaseModel):
    """Request format for Voice Detection"""
    language: str = Field(..., description="Language code e.g., 'en', 'hi'")
    audio_format: str = Field(..., alias="audioFormat", description="Format e.g., 'mp3', 'wav'")
    audio_base64: str = Field(..., alias="audioBase64", description="Base64 encoded audio string")


class VoiceResponse(BaseModel):
    """Response format for Voice Detection"""
    is_ai_generated: bool
    confidence_score: float
    details: dict = {}



class AgentResponse(BaseModel):
    """Response format required by GUVI"""
    status: Literal["success", "error"] = "success"
    reply: str


class ExtractedIntelligence(BaseModel):
    """Intelligence extracted from conversation"""
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    phoneNumbers: List[str] = Field(default_factory=list)
    suspiciousKeywords: List[str] = Field(default_factory=list)


class FinalResultPayload(BaseModel):
    """Final callback payload to GUVI endpoint"""
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str
