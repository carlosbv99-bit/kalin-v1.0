"""
Implementación de Ollama (LLM local).
Compatible con lo actual. Sin cambios de API.
"""

import requests
from typing import Optional, Dict, Any
from agent.llm.providers.base_provider import BaseLLMProvider, LLMResponse


def call_ollama(prompt: str):
    try:
        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "deepseek-coder:latest",
                "prompt": prompt,
                "stream": False,      # 🔥 SOLUCIÓN
                "num_predict": 4000
            },
            timeout=180
        )

        response.raise_for_status()
        data = response.json()

        return data.get("response", "")

    except Exception as e:
        import traceback
        traceback.print_exc()
        return None


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
                    "num_predict": 4000,
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
            text = data.get("response", "").strip()

            if not text:
                print("⚠️ Respuesta vacía de Ollama")
                print("🧠 RAW OLLAMA:", data)
                return None

            print("🧠 RAW OLLAMA:", data)
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
