"""
Mock GUVI Endpoint Server for Testing
This simulates the GUVI hackathon evaluation endpoint locally
"""
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
from datetime import datetime
import json

app = FastAPI(title="Mock GUVI Evaluation Server")

# Store received callbacks for inspection
received_callbacks = []


class ExtractedIntelligence(BaseModel):
    bankAccounts: List[str] = []
    upiIds: List[str] = []
    phishingLinks: List[str] = []
    phoneNumbers: List[str] = []
    suspiciousKeywords: List[str] = []


class FinalResultPayload(BaseModel):
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str


@app.post("/api/updateHoneyPotFinalResult")
async def receive_final_result(payload: FinalResultPayload):
    """
    Mock GUVI endpoint that receives final results
    """
    print("\n" + "="*60)
    print("📥 RECEIVED CALLBACK FROM HONEYPOT")
    print("="*60)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🆔 Session ID: {payload.sessionId}")
    print(f"🚨 Scam Detected: {payload.scamDetected}")
    print(f"💬 Total Messages: {payload.totalMessagesExchanged}")
    print("\n📊 Extracted Intelligence:")
    print(f"  💳 UPI IDs: {payload.extractedIntelligence.upiIds}")
    print(f"  🔗 Phishing Links: {payload.extractedIntelligence.phishingLinks}")
    print(f"  📞 Phone Numbers: {payload.extractedIntelligence.phoneNumbers}")
    print(f"  🏦 Bank Accounts: {payload.extractedIntelligence.bankAccounts}")
    print(f"  🔑 Keywords: {payload.extractedIntelligence.suspiciousKeywords}")
    print(f"\n📝 Agent Notes: {payload.agentNotes}")
    print("="*60 + "\n")
    
    # Store for later inspection
    received_callbacks.append({
        "timestamp": datetime.now().isoformat(),
        "payload": payload.dict()
    })
    
    # Return success response (mimicking GUVI)
    return {
        "status": "success",
        "message": "Final result received and recorded",
        "sessionId": payload.sessionId,
        "evaluation": {
            "intelligenceScore": len(payload.extractedIntelligence.upiIds) * 10 + 
                                len(payload.extractedIntelligence.phishingLinks) * 8 +
                                len(payload.extractedIntelligence.phoneNumbers) * 5,
            "engagementScore": min(100, payload.totalMessagesExchanged * 10),
            "totalScore": "Calculated based on quality metrics"
        }
    }


@app.get("/api/listCallbacks")
async def list_callbacks():
    """
    View all received callbacks
    """
    return {
        "total_callbacks": len(received_callbacks),
        "callbacks": received_callbacks
    }


@app.get("/")
async def root():
    return {
        "service": "Mock GUVI Evaluation Server",
        "endpoints": {
            "callback": "POST /api/updateHoneyPotFinalResult",
            "view_all": "GET /api/listCallbacks"
        },
        "callbacks_received": len(received_callbacks)
    }


if __name__ == "__main__":
    print("MOCK GUVI EVALUATION SERVER")
    print("="*60)
    print("Starting server on: http://localhost:9000")
    print("Endpoint: POST /api/updateHoneyPotFinalResult")
    print("View callbacks: GET /api/listCallbacks")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")
