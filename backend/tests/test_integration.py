import pytest
from app.services.chat_service import ChatService
from app.services.ingest_service import IngestService
from app.core.settings import settings
from fastapi import UploadFile, HTTPException
import io

@pytest.mark.integration
async def test_complete_rag_flow(db_session):
    """Test complete RAG flow: upload, search, and chat"""
    # Setup services
    ingest_service = IngestService(db_session)
    chat_service = ChatService(db_session)
    session = await chat_service.create_session("test-user")

    # Upload multiple documents
    docs = [
        ("doc1.txt", "Python is great for AI development."),
        ("doc2.txt", "FastAPI makes building APIs easy.")
    ]
    for filename, content in docs:
        file = UploadFile(
            filename=filename,
            file=io.BytesIO(content.encode()),
            content_type="text/plain"
        )
        await ingest_service.process_file(file, session.id)

    # Test chat with context
    messages = await chat_service.generate_response(
        session_id=session.id,
        message_content="What technologies are mentioned?"
    )

    # Verify complete flow
    assert len(messages) == 2
    assert messages[1].meta_info.get("used_chunks")
    assert any("Python" in chunk["content"] 
              for chunk in messages[1].meta_info["used_chunks"])
    assert any("FastAPI" in chunk["content"] 
              for chunk in messages[1].meta_info["used_chunks"])

@pytest.mark.integration
async def test_error_handling_flow(db_session):
    """Test error handling in the complete flow"""
    ingest_service = IngestService(db_session)
    chat_service = ChatService(db_session)
    session = await chat_service.create_session("test-user")
    
    # Test invalid file upload
    with pytest.raises(HTTPException) as exc:
        file = UploadFile(
            filename="test.xyz",
            file=io.BytesIO(b"test"),
            content_type="application/xyz"
        )
        await ingest_service.process_file(file, session.id)
    assert exc.value.status_code == 400
    
    # Test chat without context
    messages = await chat_service.generate_response(
        session_id=session.id,
        message_content="Hello"
    )
    assert len(messages) == 2
    assert not messages[1].meta_info.get("used_chunks") 