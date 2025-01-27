import pytest
from app.services.llm_service import LLMService
from app.core.settings import settings
from unittest.mock import Mock, patch

@pytest.fixture
def mock_gemini():
    with patch('google.generativeai.GenerativeModel') as mock:
        model = Mock()
        model.generate_content.return_value.text = "Test response"
        mock.return_value = model
        yield mock

@pytest.mark.asyncio
async def test_llm_response_generation(mock_gemini):
    """Test LLM response generation"""
    service = LLMService()
    messages = [
        {"role": "user", "content": "Hello"}
    ]
    
    response = await service.generate_response(messages)
    
    assert response is not None
    assert isinstance(response, str)
    mock_gemini.return_value.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_llm_system_prompt(mock_gemini):
    """Test system prompt inclusion"""
    service = LLMService()
    messages = [
        {"role": "system", "content": settings.SYSTEM_PROMPT},
        {"role": "user", "content": "Hello"}
    ]
    
    await service.generate_response(messages)
    
    call_args = mock_gemini.return_value.generate_content.call_args[0][0]
    assert settings.SYSTEM_PROMPT in call_args

@pytest.mark.asyncio
async def test_llm_parameters(mock_gemini):
    """Test LLM parameter settings"""
    service = LLMService()
    messages = [{"role": "user", "content": "Hello"}]
    
    await service.generate_response(messages)
    
    call_kwargs = mock_gemini.return_value.generate_content.call_args[1]
    assert call_kwargs.get('temperature') == settings.TEMPERATURE