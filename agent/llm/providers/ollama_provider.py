"""
Implementación de Ollama (LLM local).
Compatible con lo actual. Sin cambios de API.
"""

import requests
from typing import Optional, Dict, Any
from agent.llm.providers.base_provider import BaseLLMProvider, LLMResponse


class OllamaProvider(BaseLLMProvider):
    """Proveedor Ollama - LLM local"""

    def is_available(self) -> bool:
        """Verifica que Ollama esté corriendo"""
        try:
            response = requests.head(self.endpoint, timeout=2)
            return response.status_code < 500
        except Exception:
            return False

    def generate(self, prompt: str, max_tokens: int = 1200) -> Optional[LLMResponse]:
        """Genera respuesta usando Ollama"""
        try:
            api_url = f"{self.endpoint}/api/generate"

            response = requests.post(
                api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.2
                    }
                },
                timeout=self.timeout,
            )

            if response.status_code != 200:
                return None

            data = response.json()
            text = (data.get("response") or "").strip()

            if not text:
                return None

            return LLMResponse(
                text=text,
                provider="ollama",
                model=self.model,
                tokens_used=data.get("eval_count", 0),
                cost=0.0  # Ollama es gratis (local)
            )

        except Exception as e:
            print(f"❌ Ollama error: {e}")
            return None
