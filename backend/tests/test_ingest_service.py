import pytest
from app.services.ingest_service import IngestService
from io import BytesIO
import os
from app.core.settings import settings
from fastapi import UploadFile, HTTPException
import io
from unittest.mock import Mock, patch

@pytest.fixture
def ingest_service(db_session):
    return IngestService(db_session)

@pytest.fixture
def mock_document_service():
    with patch('app.services.document_service.DocumentService') as mock:
        doc_service = Mock()
        doc_service.process_document.return_value = Mock(id="test-doc-id")
        mock.return_value = doc_service
        yield mock

@pytest.mark.asyncio
async def test_file_processing(db_session, mock_document_service):
    """Test successful file processing"""
    service = IngestService(db_session)
    
    # Test valid file upload
    content = b"Test content"
    file = UploadFile(
        filename="test.txt",
        file=io.BytesIO(content),
        content_type="text/plain"
    )
    
    result = await service.process_file(file, "test-session")
    assert "document_id" in result
    mock_document_service.return_value.process_document.assert_called_once()

@pytest.mark.asyncio
async def test_file_validation(db_session):
    """Test file validation checks"""
    service = IngestService(db_session)
    
    # Test file size limit
    large_content = b"x" * (settings.MAX_FILE_SIZE + 1)
    large_file = UploadFile(
        filename="large.txt",
        file=io.BytesIO(large_content),
        content_type="text/plain"
    )
    with pytest.raises(HTTPException) as exc:
        await service.process_file(large_file, "test-session")
    assert exc.value.status_code == 413
    
    # Test file type validation
    invalid_file = UploadFile(
        filename="test.xyz",
        file=io.BytesIO(b"test"),
        content_type="application/xyz"
    )
    with pytest.raises(HTTPException) as exc:
        await service.process_file(invalid_file, "test-session")
    assert exc.value.status_code == 400
    assert "Unsupported file type" in str(exc.value.detail)

@pytest.mark.asyncio
async def test_ingest_errors(db_session):
    """Test ingest service error handling"""
    service = IngestService(db_session)
    
    # Test missing file
    with pytest.raises(ValueError):
        await service.process_file(None, "test-session")
    
    # Test missing session
    file = UploadFile(
        filename="test.txt",
        file=io.BytesIO(b"test"),
        content_type="text/plain"
    )
    with pytest.raises(ValueError):
        await service.process_file(file, "") 