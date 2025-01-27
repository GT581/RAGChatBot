import google.generativeai as genai
from typing import List, Any
import numpy as np
from app.core.settings import settings
import asyncio
import time

class GeminiEmbeddings:
    def __init__(self) -> None:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = settings.EMBEDDING_MODEL
        self.batch_size = settings.EMBEDDING_BATCH_SIZE
        self.request_count = 0
        self.last_request_time = time.time()

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts in batches with rate limiting"""
        embeddings: List[List[float]] = []
        
        for i in range(0, len(texts), self.batch_size):
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_request_time < 60:  # 1 minute window
                if self.request_count >= settings.MAX_RPM:
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
            embeddings.extend(batch_embeddings)

        return embeddings

    async def aembed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query text"""
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            raise

    async def aembed_query(self, text: str) -> List[float]:
        """Asynchronously get embeddings for a query"""
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            raise

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Asynchronously get embeddings for documents"""
        embeddings = []
        for text in texts:
            try:
                result = genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])
                time.sleep(1/settings.MAX_RPM)  # Rate limiting
            except Exception as e:
                print(f"Error generating embeddings: {str(e)}")
                raise
        return embeddings 