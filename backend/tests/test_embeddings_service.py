import pytest
from app.services.embeddings_service import GeminiEmbeddings
from app.core.settings import settings
from unittest.mock import Mock, patch
import numpy as np

@pytest.fixture
def mock_gemini():
    with patch('google.generativeai.GenerativeModel') as mock:
        model = Mock()
        model.embed_content.return_value.values = np.random.rand(settings.EMBEDDING_DIMENSIONS).tolist()
        mock.return_value = model
        yield mock

@pytest.mark.asyncio
async def test_embedding_dimensions(mock_gemini):
    """Test embedding dimensions and format"""
    embeddings = GeminiEmbeddings()
    
    # Test single query
    query_embedding = await embeddings.aembed_query("test query")
    assert len(query_embedding) == settings.EMBEDDING_DIMENSIONS
    assert all(isinstance(x, float) for x in query_embedding)
    
    # Test document batch
    docs = ["test doc 1", "test doc 2"]
    doc_embeddings = await embeddings.aembed_documents(docs)
    assert len(doc_embeddings) == len(docs)
    assert all(len(emb) == settings.EMBEDDING_DIMENSIONS for emb in doc_embeddings)

@pytest.mark.asyncio
async def test_rate_limiting(mock_gemini):
    """Test rate limit tracking and batching"""
    embeddings = GeminiEmbeddings()
    
    # Process multiple batches
    texts = ["test"] * (settings.EMBEDDING_BATCH_SIZE * 2)
    await embeddings.aembed_documents(texts)
    
    # Verify rate limiting
    assert embeddings.request_count == len(texts)
    assert embeddings.last_request_time > 0
    mock_gemini.return_value.embed_content.call_count == len(texts)

@pytest.mark.asyncio
async def test_embedding_errors(mock_gemini):
    """Test error handling in embedding service"""
    embeddings = GeminiEmbeddings()
    
    # Test empty input
    with pytest.raises(ValueError):
        await embeddings.aembed_query("")
    
    # Test batch size limit
    large_batch = ["test"] * (settings.EMBEDDING_BATCH_SIZE + 1)
    with pytest.raises(ValueError):
        await embeddings.aembed_documents(large_batch) 