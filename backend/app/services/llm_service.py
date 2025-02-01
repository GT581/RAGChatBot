import google.generativeai as genai
from app.core.settings import settings
from typing import List, Dict
import time
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.temperature = settings.TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS

    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> str:
        """Generate a response using the Gemini model with retry logic"""
        # Format conversation history
        conversation = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in messages
        ])
        
        for attempt in range(max_retries):
            try:
                response = await self.model.generate_content_async(
                    conversation,
                    generation_config={
                        'temperature': self.temperature,
                        'max_output_tokens': self.max_tokens,
                    }
                )
                logger.info("LLM generation successful.")
                return response.text
                
            except Exception as e:
                if attempt == max_retries - 1:
                    error_msg = f"Failed to generate response after {max_retries} attempts: {str(e)}"
                    logger.error(error_msg)
                    return "I apologize, but I'm having trouble generating a response right now. Please try again in a moment."
                else:
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2