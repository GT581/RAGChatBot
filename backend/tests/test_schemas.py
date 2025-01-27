import pytest
from app.schemas.models import (
    DocumentCreate,
    DocumentResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionResponse,
    MessageRole
)
from datetime import datetime
from uuid import UUID

def test_document_schemas():
    """Test document-related schemas"""
    # Test creation schema
    doc_data = {
        "session_id": "test-session",
        "filename": "test.txt",
        "file_type": "text/plain",
        "meta_info": {"test": "metadata"}
    }
    doc = DocumentCreate(**doc_data)
    assert doc.dict() == doc_data
    
    # Test response schema
    response_data = {
        **doc_data,
        "id": "test-id",
        "created_at": datetime.now().isoformat(),
        "chunks": []
    }
    response = DocumentResponse(**response_data)
    assert response.id == "test-id"
    assert response.chunks == []

def test_chat_message_schemas():
    """Test chat message schemas"""
    # Test creation schema
    msg_data = {
        "content": "Hello"
    }
    msg = ChatMessageCreate(**msg_data)
    assert msg.content == "Hello"
    
    # Test response schema
    response_data = {
        **msg_data,
        "id": UUID('87654321-4321-8765-4321-987654321098'),
        "created_at": datetime.now(),
        "meta_info": {"test": "metadata"}
    }
    response = ChatMessageResponse(**response_data)
    assert response.meta_info == {"test": "metadata"}

def test_chat_session_schemas():
    """Test chat session schemas"""
    # Test creation
    create_data = {
        "user_id": "test-user",
        "title": "Test Chat"
    }
    session = ChatSessionCreate(**create_data)
    assert session.user_id == "test-user"
    
    # Test response
    session_id = UUID('12345678-1234-5678-1234-567812345678')
    response_data = {
        "id": session_id,
        "user_id": "test-user",
        "title": "Test Chat",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "messages": []
    }
    response = ChatSessionResponse(**response_data)
    assert response.id == session_id
    assert response.messages == []

def test_document_schemas():
    """Test document schemas"""
    session_id = UUID('12345678-1234-5678-1234-567812345678')
    
    # Test creation
    doc_data = {
        "session_id": session_id,
        "filename": "test.txt",
        "file_type": "txt",
        "meta_info": {"size": 1024}
    }
    doc = DocumentCreate(**doc_data)
    assert doc.filename == "test.txt"
    
    # Test response
    response_data = {
        **doc_data,
        "id": UUID('87654321-4321-8765-4321-987654321098'),
        "created_at": datetime.now()
    }
    response = DocumentResponse(**response_data)
    assert response.file_type == "txt"
    assert response.meta_info["size"] == 1024

def test_schema_validations():
    """Test schema validation rules"""
    session_id = UUID('12345678-1234-5678-1234-567812345678')
    
    # Test invalid role
    with pytest.raises(ValueError):
        ChatMessageCreate(
            session_id=session_id,
            role="invalid",  # must be user/assistant/system
            content="test"
        )
    
    # Test empty content
    with pytest.raises(ValueError):
        ChatMessageCreate(
            session_id=session_id,
            role=MessageRole.USER,
            content=""  # cannot be empty
        ) 