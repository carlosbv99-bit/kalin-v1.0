"""
Implementación de Anthropic (Claude).
Para usar en cloud como fallback de OpenAI.
"""

import requests
from typing import Optional, Dict, Any
from agent.llm.providers.base_provider import BaseLLMProvider, LLMResponse


class AnthropicProvider(BaseLLMProvider):
    """Proveedor Anthropic - Claude 3.5 Sonnet, etc."""

    def is_available(self) -> bool:
        """Verifica que la API key sea válida"""
        if not self.api_key:
            return False

        try:
            response = requests.post(
                self.endpoint,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "test"}]
                },
                timeout=5
            )
            return response.status_code < 500
        except Exception:
            return False

    def generate(self, prompt: str, max_tokens: int = 1200) -> Optional[LLMResponse]:
        """Genera respuesta usando Anthropic"""
        try:
            response = requests.post(
                self.endpoint,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=self.timeout,
            )

            if response.status_code != 200:
                return None

            data = response.json()

            if "error" in data:
                print(f"❌ Anthropic error: {data['error']}")
                return None

            text = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    text = block.get("text", "").strip()
                    break

            if not text:
                return None

            # Calcula costo (aproximado)
            tokens_used = data.get("usage", {}).get("output_tokens", 0)
            cost = (tokens_used / 1000) * 0.015  # $0.015 por 1K tokens

            return LLMResponse(
                text=text,
                provider="anthropic",
                model=self.model,
                tokens_used=tokens_used,
                cost=cost
            )

        except Exception as e:
            print(f"❌ Anthropic error: {e}")
            return None
