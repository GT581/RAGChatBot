import google.generativeai as genai
from typing import List, Any
import numpy as np
from app.core.settings import settings
import asyncio
import time
import logging

logger = logging.getLogger(__name__)

class GeminiEmbeddings:
    def __init__(self) -> None:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = settings.EMBEDDING_MODEL
        self.batch_size = settings.EMBEDDING_BATCH_SIZE
        self.request_count = 0
        self.last_request_time = time.time()

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts in batches with rate limiting"""
        logger.info(f"Starting batch embedding for {len(texts)} texts")
        embeddings: List[List[float]] = []
        
        for i in range(0, len(texts), self.batch_size):
            logger.debug(f"Processing batch: texts[{i}:{i+self.batch_size}]")
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_request_time < 60:  # 1 minute window
                if self.request_count >= settings.EMBEDDING_MAX_RPM:
                    logger.warning("Rate limit reached, sleeping...")
                    await asyncio.sleep(60 - (current_time - self.last_request_time))
                    self.request_count = 0
                    self.last_request_time = time.time()
            else:
                self.request_count = 0
                self.last_request_time = current_time

            batch = texts[i:i + self.batch_size]
            batch_embeddings = [
                genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="retrieval_document"
                )['embedding']
                for text in batch
            ]
            self.request_count += len(batch)
            logger.debug(f"Generated embeddings for batch: {len(batch)} texts")
            embeddings.extend(batch_embeddings)

        logger.info("Completed generating embeddings for all texts")
        return embeddings

    async def aembed_query(self, text: str) -> List[float]:
        """Asynchronously get embeddings for a query"""
        logger.info(f"Generating embedding for query: {text[:100]}{'...' if len(text) > 100 else ''}")
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_query"
            )
            logger.info("Query embedding generation successful")
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}", exc_info=True)
            raise 