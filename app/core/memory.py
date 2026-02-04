"""
Session Memory Management
In-memory storage for conversation state
"""
import logging
from typing import Dict, List, Any
from datetime import datetime
from app.models import Message

logger = logging.getLogger(__name__)


class SessionMemory:
    """
    Simple in-memory session storage
    Stores conversation state for each sessionId
    """
    
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        logger.info("💾 SessionMemory initialized (in-memory mode)")
    
    def get_or_create_session(
        self, 
        session_id: str, 
        conversation_history: List[Message]
    ) -> Dict[str, Any]:
        """
        Get existing session or create new one
        """
        if session_id in self._sessions:
            logger.debug(f"📖 Retrieved existing session: {session_id}")
            return self._sessions[session_id]
        
        # Create new session
        session = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "turn_count": 0,
            "scam_detected": False,
            "scam_confidence": 0.0,
            "scam_type": "UNKNOWN",
            "extracted_intelligence": {
                "upiIds": [],
                "bankAccounts": [],
                "phoneNumbers": [],
                "phishingLinks": [],
                "suspiciousKeywords": []
            },
            "conversation_history": [msg.dict() for msg in conversation_history],
            "persona_state": {
                "current_persona": "elderly_rajesh",
                "confusion_level": 0.7,
                "trust_level": 0.8,
                "concern_level": 0.3
            },
            "last_message_time": datetime.now().isoformat()
        }
        
        self._sessions[session_id] = session
        logger.info(f"✨ Created new session: {session_id}")
        
        return session
    
    def update_session(self, session_id: str, session_data: Dict[str, Any]):
        """Update session data"""
        if session_id in self._sessions:
            self._sessions[session_id] = session_data
            logger.debug(f"💾 Updated session: {session_id}")
        else:
            logger.warning(f"⚠️ Attempted to update non-existent session: {session_id}")
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session by ID"""
        return self._sessions.get(session_id)
    
    def delete_session(self, session_id: str):
        """Delete session (cleanup)"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"🗑️ Deleted session: {session_id}")
    
    def list_active_sessions(self) -> List[str]:
        """Get list of all active session IDs"""
        return list(self._sessions.keys())
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        return len(self._sessions)
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Remove sessions older than specified hours"""
        now = datetime.now()
        to_delete = []
        
        for session_id, session in self._sessions.items():
            created_at = datetime.fromisoformat(session["created_at"])
            age_hours = (now - created_at).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                to_delete.append(session_id)
        
        for session_id in to_delete:
            self.delete_session(session_id)
        
        if to_delete:
            logger.info(f"🧹 Cleaned up {len(to_delete)} old sessions")
        
        return len(to_delete)
