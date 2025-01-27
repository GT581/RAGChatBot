import pytest
from app.db.models import Document, DocumentChunk, ChatSession, ChatMessage
from app.core.settings import settings
import numpy as np
from datetime import datetime

def test_document_model(db_session):
    """Test Document model relationships and constraints"""
    # Create document
    doc = Document(
        session_id="test-session",
        filename="test.txt",
        file_type="text/plain",
        meta_info={"test": "metadata"}
    )
    db_session.add(doc)
    db_session.commit()
    
    # Test basic attributes
    assert doc.id is not None
    assert doc.created_at is not None
    assert isinstance(doc.created_at, datetime)
    assert doc.meta_info == {"test": "metadata"}
    
    # Test relationships
    assert doc.chunks == []

def test_document_chunk_model(db_session):
    """Test DocumentChunk model with embeddings"""
    # Create parent document
    doc = Document(
        session_id="test-session",
        filename="test.txt",
        file_type="text/plain"
    )
    db_session.add(doc)
    db_session.commit()
    
    # Create chunk with embedding
    embedding = np.random.rand(settings.EMBEDDING_DIMENSIONS).tolist()
    chunk = DocumentChunk(
        document_id=doc.id,
        content="Test content",
        chunk_index=0,
        embedding=embedding,
        meta_info={"index": 0}
    )
    db_session.add(chunk)
    db_session.commit()
    
    # Test relationships and attributes
    assert chunk.document == doc
    assert len(chunk.embedding) == settings.EMBEDDING_DIMENSIONS
    assert chunk.chunk_index == 0
    assert chunk.meta_info == {"index": 0}

def test_chat_models(db_session):
    """Test ChatSession and ChatMessage models"""
    # Create session
    session = ChatSession(
        user_id="test-user",
        title="Test Chat"
    )
    db_session.add(session)
    db_session.commit()
    
    # Test session attributes
    assert session.id is not None
    assert session.created_at is not None
    assert not session.hidden
    
    # Add messages
    messages = [
        ChatMessage(
            session_id=session.id,
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}",
            meta_info={"test": i}
        )
        for i in range(3)
    ]
    db_session.add_all(messages)
    db_session.commit()
    
    # Test relationships and ordering
    assert len(session.messages) == 3
    assert all(msg.created_at is not None for msg in session.messages)
    assert [msg.role for msg in session.messages] == ["user", "assistant", "user"]

def test_model_constraints(db_session):
    """Test model constraints and relationships"""
    # Test cascade delete
    session = ChatSession(user_id="test-user")
    db_session.add(session)
    db_session.commit()
    
    message = ChatMessage(
        session_id=session.id,
        role="user",
        content="test"
    )
    db_session.add(message)
    db_session.commit()
    
    # Delete session should cascade to messages
    db_session.delete(session)
    db_session.commit()
    
    # Message should be deleted
    assert db_session.query(ChatMessage).filter_by(
        session_id=session.id
    ).first() is None 