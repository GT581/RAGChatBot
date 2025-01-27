import pytest
from app.services.document_service import DocumentService
from app.db.models import Document, DocumentChunk
from app.core.settings import settings
from unittest.mock import Mock, patch
import io

@pytest.fixture
def mock_embeddings():
    with patch('app.services.embeddings_service.GeminiEmbeddings') as mock:
        embedder = Mock()
        embedder.aembed_documents.return_value = [
            [0.1] * settings.EMBEDDING_DIMENSIONS
        ]
        embedder.aembed_query.return_value = [0.1] * settings.EMBEDDING_DIMENSIONS
        mock.return_value = embedder
        yield mock

@pytest.mark.asyncio
async def test_document_processing(db_session, mock_embeddings):
    """Test document processing with different file types"""
    service = DocumentService(db_session)
    
    # Test text processing
    text_doc = await service.process_document(
        session_id="test-session",
        file_content="Test content\nMore content",
        filename="test.txt",
        file_type="text/plain"
    )
    assert text_doc.filename == "test.txt"
    assert text_doc.file_type == "text/plain"
    assert len(text_doc.chunks) > 0
    assert all(len(chunk.embedding) == settings.EMBEDDING_DIMENSIONS 
              for chunk in text_doc.chunks)
    
    # Test PDF processing
    pdf_doc = await service.process_document(
        session_id="test-session",
        file_content=b"%PDF-1.4\n%%EOF",
        filename="test.pdf",
        file_type="application/pdf"
    )
    assert pdf_doc.filename == "test.pdf"
    assert pdf_doc.file_type == "application/pdf"
    assert len(pdf_doc.chunks) > 0
    assert all(len(chunk.embedding) == settings.EMBEDDING_DIMENSIONS 
              for chunk in pdf_doc.chunks)

@pytest.mark.asyncio
async def test_vector_search(db_session, mock_embeddings):
    """Test vector similarity search"""
    service = DocumentService(db_session)
    
    # Create test document with chunks
    document = await service.process_document(
        session_id="test-session",
        file_content="Test content for search",
        filename="test.txt",
        file_type="text/plain"
    )
    
    # Test similarity search
    chunks, scores = await service.search_similar_chunks(
        query="test query",
        session_id="test-session",
        limit=settings.SIMILARITY_TOP_K
    )
    
    # Verify search results
    assert len(chunks) <= settings.SIMILARITY_TOP_K
    assert len(chunks) == len(scores)
    assert all(0 <= score <= 1 for score in scores)
    assert all(chunk.document_id == document.id for chunk in chunks)

@pytest.mark.asyncio
async def test_document_errors(db_session, mock_embeddings):
    """Test document service error handling"""
    service = DocumentService(db_session)
    
    # Test invalid session
    with pytest.raises(ValueError):
        await service.process_document(
            session_id="",
            file_content="test",
            filename="test.txt",
            file_type="text/plain"
        )
    
    # Test empty content
    with pytest.raises(ValueError):
        await service.process_document(
            session_id="test-session",
            file_content="",
            filename="test.txt",
            file_type="text/plain"
        )
    
    # Test invalid search
    with pytest.raises(ValueError):
        await service.search_similar_chunks(
            query="",
            session_id="test-session"
        ) 