from pydantic import BaseModel

class SetModelRequest(BaseModel):
    provider: str  # e.g., "openai", "anthropic", "gemini", "local"
    model: str     # e.g., "gpt-4o", "claude-sonnet-4-5-20250929", "gemini-3-flash-preview", "microsoft/Phi-3-mini-4k-instruct"
    api_key: str = None