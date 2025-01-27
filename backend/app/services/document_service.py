from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from ..db.models import Document, DocumentChunk
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..services.embeddings_service import GeminiEmbeddings
from app.core.settings import settings
import PyPDF2
import pandas as pd
import json
import io
import uuid
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.embeddings = GeminiEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

    def read_file_content(self, content: bytes, content_type: str) -> str:
        """Extract text content from various file types"""
        try:
            if content_type == 'application/pdf':
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                return "\n".join(page.extract_text() for page in pdf_reader.pages)
            
            elif content_type == 'text/csv':
                df = pd.read_csv(io.BytesIO(content))
                return df.to_string()
            
            elif content_type == 'application/json':
                return json.dumps(json.loads(content.decode()), indent=2)
            
            elif content_type.startswith('application/vnd.openxmlformats'):
                df = pd.read_excel(io.BytesIO(content))
                return df.to_string()
            
            return content.decode('utf-8')
        except Exception as e:
            logger.error(f"Error reading file content: {str(e)}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    async def process_document(self, session_id: str, file_content: str, filename: str, file_type: str):
        """Process a document: create chunks and generate embeddings"""
        # Create document record
        document = Document(
            session_id=session_id,
            filename=filename,
            file_type=file_type,
            meta_info={}
        )
        self.db.add(document)
        self.db.commit()
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(file_content)
        
        # Prepare chunks for batch processing
        chunk_texts = []
        db_chunks = []
        
        for i, chunk_content in enumerate(chunks):
            chunk_texts.append(chunk_content)
            chunk = DocumentChunk(
                document_id=document.id,
                content=chunk_content,
                chunk_index=i
            )
            db_chunks.append(chunk)
        
        # Generate embeddings in batch
        embeddings = await self.embeddings.aembed_documents(chunk_texts)
        
        # Store chunks with embeddings
        for chunk, embedding in zip(db_chunks, embeddings):
            chunk.embedding = embedding
            self.db.add(chunk)
        
        self.db.commit()
        return document

    async def search_similar_chunks(self, query: str, session_id: str, limit: int | None = None) -> tuple[List[DocumentChunk], List[float]]:
        """Search for similar chunks using vector similarity and return chunks with their scores"""
        limit = limit or settings.SIMILARITY_TOP_K
        query_embedding = await self.embeddings.aembed_query(query)
        
        # Use SQLAlchemy text() for raw SQL
        stmt = text("""
        SELECT id, (embedding <-> CAST(:query_embedding AS vector)) as distance
        FROM document_chunks
        ORDER BY embedding <-> CAST(:query_embedding AS vector)
        LIMIT :limit
        """)
        
        result = self.db.execute(
            stmt,
            {
                "query_embedding": query_embedding,
                "limit": limit
            }
        ).fetchall()
        
        chunk_ids = []
        scores = []
        for row in result:
            chunk_ids.append(row[0])
            scores.append(float(row[1]))
        
        chunks = self.db.query(DocumentChunk).filter(
            DocumentChunk.id.in_(chunk_ids)
        ).all()
        
        # Maintain order from similarity search
        id_to_chunk = {str(chunk.id): chunk for chunk in chunks}
        return [id_to_chunk[str(chunk_id)] for chunk_id in chunk_ids], scores 