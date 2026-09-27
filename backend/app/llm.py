"""Small provider boundary. Without an API key callers should use truthful local behavior."""
from app.config import settings

class LLMUnavailable(RuntimeError): pass

class LLMProvider:
    async def generate(self, prompt: str) -> str:
        raise NotImplementedError

class OpenAIProvider(LLMProvider):
    async def generate(self, prompt: str) -> str:
        if not settings.openai_api_key:
            raise LLMUnavailable("No LLM provider is configured")
        import httpx
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post("https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={"model": settings.openai_model, "messages": [{"role": "user", "content": prompt}]})
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
