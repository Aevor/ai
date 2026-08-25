import httpx
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError
from services.core.config import settings
from models.base import BaseModelProvider

T = TypeVar("T", bound=BaseModel)

class GeminiConfigError(ValueError):
    """Raised when the Gemini API key is missing or invalid."""
    pass

class GeminiResponseError(RuntimeError):
    """Raised when the Gemini API returns an error or invalid response."""
    pass

class GeminiProvider(BaseModelProvider):
    """Implements the BaseModelProvider contract for the Google Gemini REST API."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL

    def _convert_schema(self, schema: dict) -> dict:
        """Translates standard JSON schema types into Gemini-compatible uppercase OpenAPI types."""
        type_mapping = {
            "string": "STRING",
            "object": "OBJECT",
            "array": "ARRAY",
            "integer": "INTEGER",
            "boolean": "BOOLEAN",
            "number": "NUMBER"
        }

        cleaned = {}
        if "type" in schema:
            raw_type = schema["type"]
            cleaned["type"] = type_mapping.get(raw_type, "TYPE_UNSPECIFIED")

        if "description" in schema:
            cleaned["description"] = schema["description"]

        if cleaned.get("type") == "OBJECT":
            if "properties" in schema:
                cleaned["properties"] = {
                    k: self._convert_schema(v) for k, v in schema["properties"].items()
                }
            if "required" in schema:
                cleaned["required"] = schema["required"]
        elif cleaned.get("type") == "ARRAY":
            if "items" in schema:
                cleaned["items"] = self._convert_schema(schema["items"])

        return cleaned

    async def generate_structured(
        self,
        prompt: str,
        system_instruction: str,
        response_schema: Type[T]
    ) -> T:
        """Sends an asynchronous request to the Gemini REST API and parses the structured response."""
        if not self.api_key:
            raise GeminiConfigError("Gemini API key is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        gemini_schema = self._convert_schema(response_schema.model_json_schema())

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "systemInstruction": {
                "parts": [
                    {"text": system_instruction}
                ]
            },
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": gemini_schema,
                "temperature": 0.1
            }
        }

        params = {"key": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, params=params)

            if response.status_code != 200:
                raise GeminiResponseError(
                    f"Gemini API call failed with status code {response.status_code}: {response.text}"
                )

            response_data = response.json()

            try:
                candidate = response_data["candidates"][0]
                text_content = candidate["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as err:
                raise GeminiResponseError(
                    f"Invalid Gemini response structure: {response_data}"
                ) from err

            try:
                return response_schema.model_validate_json(text_content)
            except ValidationError as err:
                raise GeminiResponseError(
                    f"Generated content failed validation against schema: {text_content}"
                ) from err

        except httpx.HTTPError as err:
            raise GeminiResponseError(f"HTTP communication with Gemini failed: {err}") from err
