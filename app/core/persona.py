"""
Persona Management System
Implements "Elderly Rajesh" character with consistent responses
"""
import logging
import random
from typing import Dict, Any, List
from app.models import Message

logger = logging.getLogger(__name__)


class PersonaManager:
    """
    Manages AI persona for engaging with scammers
    MVP: Single persona (Elderly Rajesh)
    """
    
    def __init__(self):
        self.current_persona = "elderly_rajesh"
        logger.info(f"🎭 PersonaManager initialized with persona: {self.current_persona}")
    
    async def generate_response(
        self,
        scammer_message: str,
        session: Dict[str, Any],
        conversation_history: List[Message]
    ) -> str:
        """
        Generate persona-appropriate response
        
        Strategy:
        - Try LLM first (if available)
        - Fall back to rule-based responses
        - Maintain elderly character
        - Show confusion about technology
        - Ask clarifying questions
        - Delay providing information
        - Elicit more details from scammer
        """
        turn_count = session["turn_count"]
        scam_type = session.get("scam_type", "UNKNOWN")
        
        # Analyze scammer's message for context
        message_lower = scammer_message.lower()
        
        # Try LLM-enhanced response first
        llm_response = await self._try_llm_response(
            scammer_message,
            turn_count,
            scam_type,
            conversation_history
        )
        
        if llm_response:
            logger.debug(f"🤖 Generated LLM response (turn {turn_count}): {llm_response[:50]}...")
            return llm_response
        
        # Fallback to rule-based response
        response = self._select_response_strategy(
            message_lower,
            turn_count,
            scam_type,
            session
        )
        
        logger.debug(f"🎭 Generated rule-based response (turn {turn_count}): {response[:50]}...")
        
        return response
    
    async def _try_llm_response(
        self,
        scammer_message: str,
        turn_count: int,
        scam_type: str,
        conversation_history: List[Message]
    ) -> str:
        """
        Try to generate response using LLM (Groq)
        Returns None if LLM not available or fails
        """
        try:
            from app.config import settings
            
            # Only use LLM if Groq is configured
            if settings.LLM_PROVIDER != "groq" or not settings.GROQ_API_KEY:
                return None
            
            import httpx
            
            # Build conversation context
            system_prompt = (
                "You are Rajesh, a 65-year-old retired schoolteacher from Mumbai. "
                "You're not very familiar with technology, smartphones, or online banking. "
                "You're cautious but confused about modern scams. Keep responses natural, "
                "short (2-3 sentences), show confusion, ask clarifying questions, and "
                "delay giving information. Never provide real financial details."
            )
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": scammer_message}
            ]
            
            # Call Groq API
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.LLM_MODEL,
                        "messages": messages,
                        "temperature": 0.8,
                        "max_tokens": 150
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    llm_reply = result["choices"][0]["message"]["content"].strip()
                    return llm_reply
                else:
                    logger.warning(f"LLM API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.debug(f"LLM generation failed (using fallback): {str(e)}")
            return None
    
    def _select_response_strategy(
        self,
        message: str,
        turn_count: int,
        scam_type: str,
        session: Dict[str, Any]
    ) -> str:
        """Select appropriate response based on context"""
        
        # First response - show confusion and concern
        if turn_count == 0:
            return self._initial_response(message, scam_type)
        
        # If scammer asks for UPI
        if any(word in message for word in ["upi", "payment", "transfer", "send money"]):
            return self._respond_to_upi_request(turn_count)
        
        # If scammer shares link
        if any(word in message for word in ["link", "click", "website", "http", "bit.ly"]):
            return self._respond_to_link(turn_count)
        
        # If scammer asks for OTP or sensitive info
        if any(word in message for word in ["otp", "code", "password", "pin", "cvv"]):
            return self._respond_to_sensitive_request()
        
        # If scammer creates urgency
        if any(word in message for word in ["urgent", "immediately", "now", "today", "blocked"]):
            return self._respond_to_urgency(turn_count)
        
        # If scammer asks for bank account
        if any(word in message for word in ["account", "bank", "account number"]):
            return self._respond_to_account_request(turn_count)
        
        # If scammer mentions fee or payment
        if any(word in message for word in ["fee", "pay", "charge", "amount", "₹", "rupees"]):
            return self._respond_to_fee_request(turn_count)
        
        # Generic confused response
        return self._generic_confused_response(turn_count)
    
    def _initial_response(self, message: str, scam_type: str) -> str:
        """First response to establish persona"""
        responses = [
            "Beta, what is this? I don't understand. Why are you saying this?",
            "What happened? Is there some problem? I'm not understanding what you're saying.",
            "Hello? I'm old person, I don't know about these things. Can you explain simply?",
            "What is the matter? I am confused. Please tell me clearly what is the issue.",
            "I don't understand these technical words. Can you explain to me like a simple person?"
        ]
        return random.choice(responses)
    
    def _respond_to_upi_request(self, turn_count: int) -> str:
        """Response when scammer asks for UPI"""
        if turn_count < 3:
            responses = [
                "What is UPI? I only use cash. My son handles my phone.",
                "UPI means what? I don't have smartphone, only Nokia button phone.",
                "I don't know about UPI. Can I just go to bank branch? That is easier for me.",
                "My grandson set up some payment thing, but I don't know how to use it. What should I do?"
            ]
        else:
            responses = [
                "Wait, let me ask my son about UPI. Which app should I use?",
                "I have some payment app but I forgot the password. Can you tell me which bank you are from?",
                "My UPI... I think it's something with my name. But which one you need? I have many banks.",
                "Beta, which UPI handle you want? I have SBI and HDFC both. Tell me your employee ID first."
            ]
        return random.choice(responses)
    
    def _respond_to_link(self, turn_count: int) -> str:
        """Response when scammer shares link"""
        responses = [
            "Link? How do I open link? My phone doesn't have internet. Can you come to my house?",
            "I can't click anything. My phone is very old. Can you just tell me what to do?",
            "My grandson said never click on any link. Are you really from the company?",
            "I don't know how to click. My hands shake. Can you send someone to help me?",
            "The link is not opening. My phone doesn't have data. What should I do now?"
        ]
        return random.choice(responses)
    
    def _respond_to_sensitive_request(self) -> str:
        """Response when scammer asks for OTP/password"""
        responses = [
            "OTP means what? I don't get any message. My phone is basic phone.",
            "My son told me never share password with anyone. Are you from my bank really?",
            "I don't see any code. Maybe my phone is not working? What number did you send to?",
            "PIN? I only remember my ATM PIN for withdrawing cash. Is that what you need?",
            "I don't know about these security codes. Can I just visit the bank tomorrow?"
        ]
        return random.choice(responses)
    
    def _respond_to_urgency(self, turn_count: int) -> str:
        """Response when scammer creates urgency"""
        if turn_count < 2:
            responses = [
                "Why so urgent? What will happen? I'm getting worried now. Please tell me clearly.",
                "Oh no! What should I do? I'm alone at home. Should I call my son?",
                "Today itself? But I don't understand the problem. Why urgent?",
                "I'm getting scared. What will happen if I don't do it? Please explain properly."
            ]
        else:
            responses = [
                "But I need time to understand. I'm old person, can't do things so fast.",
                "You're making me nervous. Let me first call bank customer care to confirm.",
                "Why are you rushing me? This sounds suspicious. My son warned me about fraud calls.",
                "Hold on, I want to verify this first. Give me your employee ID and supervisor number."
            ]
        return random.choice(responses)
    
    def _respond_to_account_request(self, turn_count: int) -> str:
        """Response when asked for bank account"""
        responses = [
            "I have accounts in 3 banks. Which bank are you calling from? SBI or HDFC or ICICI?",
            "Account number? I have my passbook somewhere. Wait, let me find it. Which bank you said?",
            "I don't remember account number. It's written in my passbook. Are you really from bank?",
            "First tell me, why you need my account number? My son said never share on phone.",
            "Which account? I have savings and pension account both. Tell me your office address first."
        ]
        return random.choice(responses)
    
    def _respond_to_fee_request(self, turn_count: int) -> str:
        """Response when scammer mentions fee/payment"""
        responses = [
            "Fee for what? Nobody told me about any fee. How much is it?",
            "I have to pay money? But why? I thought you are helping me. This is confusing.",
            "How much fee? Can I pay at bank branch? I don't trust online payment.",
            "You want me to pay? But you called me saying my account has problem. Why I should pay?",
            "My son said never pay any fee on phone. Are you doing some fraud? Tell me truth."
        ]
        return random.choice(responses)
    
    def _generic_confused_response(self, turn_count: int) -> str:
        """Generic confused elderly responses"""
        responses = [
            "I'm not understanding what you're saying. Can you speak slowly?",
            "Beta, you're using too many English words. I'm simple person from village.",
            "What you are saying is too complicated for me. Can you explain in simple way?",
            "I'm getting more confused. Maybe I should ask my neighbor who knows computers.",
            "You're talking too fast. I'm old, my hearing is not good. Say again please.",
            "I don't know about all these modern things. Why don't you just send someone to my house?",
            "This is very confusing for me. Let me call my son, he will talk to you.",
            "I need to think about this. Can you call me tomorrow? I will ask my family."
        ]
        return random.choice(responses)
