"""
Implementación de OpenAI (GPT-4, GPT-3.5).
Para usar en cloud/producción.
"""

import requests
from typing import Optional, Dict, Any
from agent.llm.providers.base_provider import BaseLLMProvider, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    """Proveedor OpenAI - GPT-4, GPT-3.5-turbo, etc."""

    def is_available(self) -> bool:
        """Verifica que la API key sea válida"""
        if not self.api_key:
            return False

        try:
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, max_tokens: int = 1200) -> Optional[LLMResponse]:
        """Genera respuesta usando OpenAI"""
        try:
            response = requests.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.2,
                },
                timeout=self.timeout,
            )

            if response.status_code != 200:
                return None

            data = response.json()
            
            if "error" in data:
                print(f"❌ OpenAI error: {data['error']}")
                return None

            text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

            if not text:
                return None

            # Calcula costo (aproximado)
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            cost = (tokens_used / 1000) * 0.03  # $0.03 por 1K tokens

            return LLMResponse(
                text=text,
                provider="openai",
                model=self.model,
                tokens_used=tokens_used,
                cost=cost
            )

        except Exception as e:
            print(f"❌ OpenAI error: {e}")
            return None
