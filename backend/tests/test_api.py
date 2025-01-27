import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.settings import settings
import io

@pytest.fixture
def client():
    return TestClient(app)

def test_api_endpoints(client):
    """Test API endpoint availability"""
    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200
    
    # Test API version endpoint
    response = client.get(f"{settings.API_V1_STR}/openapi.json")
    assert response.status_code == 200

def test_chat_endpoints(client):
    """Test chat API endpoints"""
    # Create session
    response = client.post(f"{settings.API_V1_STR}/chat/session")
    assert response.status_code == 200
    session_data = response.json()
    session_id = session_data["id"]
    
    # Send message
    response = client.post(
        f"{settings.API_V1_STR}/chat/message",
        json={
            "session_id": session_id,
            "content": "Hello"
        }
    )
    assert response.status_code == 200
    assert "role" in response.json()
    assert "content" in response.json()
    
    # Get sessions
    response = client.get(f"{settings.API_V1_STR}/chat/sessions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_file_upload_endpoints(client):
    """Test file upload endpoints"""
    # Test valid upload
    content = b"Test content"
    files = {
        "file": ("test.txt", io.BytesIO(content), "text/plain")
    }
    data = {"session_id": "test-session"}
    
    response = client.post(
        f"{settings.API_V1_STR}/ingest/upload",
        files=files,
        data=data
    )
    assert response.status_code == 200
    assert "document_id" in response.json()
    
    # Test invalid file type
    files = {
        "file": ("test.xyz", io.BytesIO(b"test"), "application/xyz")
    }
    response = client.post(
        f"{settings.API_V1_STR}/ingest/upload",
        files=files,
        data=data
    )
    assert response.status_code == 400 

def test_api_error_handling(client):
    """Test API error responses"""
    # Test invalid session ID
    response = client.post(
        f"{settings.API_V1_STR}/chat/message",
        json={
            "session_id": "invalid-id",
            "content": "Hello"
        }
    )
    assert response.status_code == 404
    
    # Test missing file in upload
    response = client.post(
        f"{settings.API_V1_STR}/ingest/upload",
        files={},
        data={"session_id": "test-session"}
    )
    assert response.status_code == 422
    
    # Test invalid content type
    response = client.post(
        f"{settings.API_V1_STR}/chat/message",
        data="invalid-json"
    )
    assert response.status_code == 422 