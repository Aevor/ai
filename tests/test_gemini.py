import pytest
from unittest.mock import AsyncMock, patch
import httpx
from models.schemas import PRSummary
from models.gemini import GeminiProvider, GeminiConfigError, GeminiResponseError

@pytest.fixture
def anyio_backend():
    """Specifies asyncio as the backend for anyio async tests."""
    return "asyncio"

@pytest.mark.anyio
async def test_gemini_provider_success():
    mock_response_data = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": '{"summary": "A clean fix for routing", "key_changes": ["Added a crash-test route", "Tested global error handling"], "review_focus": ["services/main.py"]}'
                        }
                    ]
                }
            }
        ]
    }

    mock_post = AsyncMock()
    mock_post.return_value = httpx.Response(200, json=mock_response_data)

    with patch("httpx.AsyncClient.post", mock_post):
        provider = GeminiProvider(api_key="test-key", model="gemini-2.5-flash")
        result = await provider.generate_structured(
            prompt="summarize diff",
            system_instruction="you are a helpful assistant",
            response_schema=PRSummary
        )

    assert result.summary == "A clean fix for routing"
    assert result.key_changes == ["Added a crash-test route", "Tested global error handling"]
    assert result.review_focus == ["services/main.py"]

    mock_post.assert_called_once()
    called_url, called_kwargs = mock_post.call_args
    assert "generativelanguage.googleapis.com" in str(called_url[0])
    assert called_kwargs["params"] == {"key": "test-key"}

    payload = called_kwargs["json"]
    assert payload["contents"][0]["parts"][0]["text"] == "summarize diff"
    assert payload["systemInstruction"]["parts"][0]["text"] == "you are a helpful assistant"
    assert payload["generationConfig"]["responseMimeType"] == "application/json"
    assert payload["generationConfig"]["responseSchema"]["type"] == "OBJECT"

@pytest.mark.anyio
async def test_gemini_provider_missing_key():
    # Empty API key should raise GeminiConfigError
    provider = GeminiProvider(api_key="", model="gemini-2.5-flash")
    with pytest.raises(GeminiConfigError) as exc_info:
        await provider.generate_structured("diff", "system", PRSummary)
    assert "Gemini API key is not configured" in str(exc_info.value)

@pytest.mark.anyio
async def test_gemini_provider_http_error():
    mock_post = AsyncMock()
    mock_post.return_value = httpx.Response(500, text="Internal Server Error")

    with patch("httpx.AsyncClient.post", mock_post):
        provider = GeminiProvider(api_key="test-key", model="gemini-2.5-flash")
        with pytest.raises(GeminiResponseError) as exc_info:
            await provider.generate_structured("diff", "system", PRSummary)
        assert "Gemini API call failed with status code 500" in str(exc_info.value)

@pytest.mark.anyio
async def test_gemini_provider_malformed_json_response():
    mock_response_data = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": '{"summary": "Incomplete JSON...'
                        }
                    ]
                }
            }
        ]
    }

    mock_post = AsyncMock()
    mock_post.return_value = httpx.Response(200, json=mock_response_data)

    with patch("httpx.AsyncClient.post", mock_post):
        provider = GeminiProvider(api_key="test-key", model="gemini-2.5-flash")
        with pytest.raises(GeminiResponseError) as exc_info:
            await provider.generate_structured("diff", "system", PRSummary)
        assert "Generated content failed validation against schema" in str(exc_info.value)
