import pytest
from app.services.chat_service import ChatService
from app.db.models import ChatSession, ChatMessage
from app.core.settings import settings
from unittest.mock import Mock, patch

@pytest.fixture
def mock_llm():
    with patch('app.services.llm_service.LLMService') as mock:
        llm = Mock()
        llm.generate_response.return_value = "Test response"
        mock.return_value = llm
        yield mock

@pytest.fixture
def mock_document_service():
    with patch('app.services.document_service.DocumentService') as mock:
        doc_service = Mock()
        doc_service.search_similar_chunks.return_value = ([], [])
        mock.return_value = doc_service
        yield mock

@pytest.mark.asyncio
async def test_chat_session_management(db_session):
    """Test chat session CRUD operations"""
    service = ChatService(db_session)
    
    # Create & Read
    session = await service.create_session("test-user")
    assert session.user_id == "test-user"
    
    retrieved = service.get_session(session.id)
    assert retrieved.id == session.id
    
    # List sessions
    sessions = service.get_user_sessions("test-user")
    assert len(sessions) == 1
    assert sessions[0].id == session.id
    
    # Update title
    message = ChatMessage(
        session_id=session.id,
        role="user",
        content="Test message"
    )
    db_session.add(message)
    db_session.commit()
    await service.update_session_title(session.id)
    assert "Test message" in session.title
    
    # Delete (hide)
    await service.delete_session(session.id)
    assert service.get_session(session.id).hidden

@pytest.mark.asyncio
async def test_chat_response_generation(db_session, mock_llm, mock_document_service):
    """Test chat response with context and system prompt"""
    service = ChatService(db_session)
    session = await service.create_session("test-user")
    
    messages = await service.generate_response(
        session_id=session.id,
        message_content="Test question"
    )
    
    # Check message flow
    assert len(messages) == 2  # User message and response
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
    
    # Verify service calls
    mock_llm.return_value.generate_response.assert_called_once()
    mock_document_service.return_value.search_similar_chunks.assert_called_once()
    
    # Verify system prompt
    llm_call = mock_llm.return_value.generate_response.call_args[0][0]
    assert any(msg.get("role") == "system" and 
              msg.get("content") == settings.SYSTEM_PROMPT 
              for msg in llm_call)

@pytest.mark.asyncio
async def test_chat_history_management(db_session):
    """Test chat history with limits"""
    service = ChatService(db_session)
    session = await service.create_session("test-user")
    
    # Add more messages than MAX_HISTORY
    for i in range(settings.MAX_HISTORY + 5):
        message = ChatMessage(
            session_id=session.id,
            role="user",
            content=f"Message {i}"
        )
        db_session.add(message)
    db_session.commit()
    
    history = service.get_chat_history(session.id)
    assert len(history) <= settings.MAX_HISTORY