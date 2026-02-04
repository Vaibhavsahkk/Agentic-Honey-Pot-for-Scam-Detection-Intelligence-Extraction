"""
Final Result Callback Handler
Sends extracted intelligence to GUVI evaluation endpoint
"""
import logging
import asyncio
import httpx
from app.models import FinalResultPayload
from app.config import settings

logger = logging.getLogger(__name__)


async def send_final_result(payload: FinalResultPayload, max_retries: int = 3) -> bool:
    """
    Send final extraction results to GUVI endpoint with retry logic
    
    This is MANDATORY for hackathon evaluation
    
    Args:
        payload: Final result data
        max_retries: Number of retry attempts (default: 3)
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("="*60)
    logger.info(f"📤 SENDING FINAL RESULT TO GUVI")
    logger.info("="*60)
    logger.info(f"🆔 Session: {payload.sessionId}")
    logger.info(f"🚨 Scam Detected: {payload.scamDetected}")
    logger.info(f"💬 Messages Exchanged: {payload.totalMessagesExchanged}")
    logger.info(f"📊 Intelligence Summary:")
    logger.info(f"   💳 UPI IDs: {len(payload.extractedIntelligence.upiIds)}")
    logger.info(f"   🔗 Links: {len(payload.extractedIntelligence.phishingLinks)}")
    logger.info(f"   📞 Phones: {len(payload.extractedIntelligence.phoneNumbers)}")
    logger.info(f"   🏦 Accounts: {len(payload.extractedIntelligence.bankAccounts)}")
    logger.info(f"📍 Endpoint: {settings.GUVI_CALLBACK_URL}")
    logger.info("="*60)
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"🔄 Attempt {attempt}/{max_retries}...")
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    settings.GUVI_CALLBACK_URL,
                    json=payload.dict(),
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    logger.info("="*60)
                    logger.info(f"✅ SUCCESS! Final result accepted by GUVI")
                    logger.info(f"📥 Response: {response.text[:200]}")
                    logger.info("="*60)
                    return True
                else:
                    logger.warning(
                        f"⚠️ Attempt {attempt} failed: "
                        f"Status {response.status_code}, "
                        f"Response: {response.text[:200]}"
                    )
                    
                    # Don't retry on client errors (4xx)
                    if 400 <= response.status_code < 500:
                        logger.error("❌ Client error - not retrying")
                        break
                        
        except httpx.TimeoutException:
            logger.warning(f"⏱️ Attempt {attempt} timed out (15s)")
        except httpx.RequestError as e:
            logger.warning(f"🔌 Attempt {attempt} network error: {str(e)}")
        except Exception as e:
            logger.error(f"💥 Attempt {attempt} unexpected error: {str(e)}", exc_info=True)
        
        # Wait before retry (exponential backoff)
        if attempt < max_retries:
            wait_time = 2 ** attempt  # 2, 4, 8 seconds
            logger.info(f"⏳ Waiting {wait_time}s before retry...")
            await asyncio.sleep(wait_time)
    
    logger.error("="*60)
    logger.error(f"❌ FAILED to send final result after {max_retries} attempts")
    logger.error(f"Session: {payload.sessionId}")
    logger.error("="*60)
    return False


def send_final_result_sync(payload: FinalResultPayload) -> bool:
    """
    Synchronous version of send_final_result (for non-async contexts)
    """
    import requests
    
    try:
        logger.info(f"📤 Sending final result (sync) for session: {payload.sessionId}")
        
        response = requests.post(
            settings.GUVI_CALLBACK_URL,
            json=payload.dict(),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Final result sent successfully for {payload.sessionId}")
            return True
        else:
            logger.error(
                f"❌ Failed to send final result. "
                f"Status: {response.status_code}"
            )
            return False
            
    except Exception as e:
        logger.error(f"💥 Error sending final result: {str(e)}", exc_info=True)
        return False
