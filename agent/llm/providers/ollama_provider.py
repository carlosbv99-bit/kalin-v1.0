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

    def generate(self, prompt: str, max_tokens: int = 1200, temperature: float = None) -> Optional[LLMResponse]:
        """
        Genera respuesta usando Ollama
        
        Args:
            prompt: Texto a procesar
            max_tokens: Máximo tokens a generar
            temperature: Temperatura (0.0-1.0). Si es None, usa default según tipo de modelo
        """
        try:
            # Detectar si es modelo de chat y usar endpoint apropiado
            is_chat_model = "chat" in self.model or "qwen" in self.model.lower() or "llama" in self.model.lower()
            
            # Usar temperatura proporcionada o defaults
            if temperature is None:
                temperature = 0.9 if is_chat_model else 0.2
            
            if is_chat_model:
                # Usar endpoint /api/chat para modelos conversacionales
                api_url = f"{self.endpoint}/api/chat"
                
                # Detectar si es HTML para usar configuración optimizada (más rápida)
                es_html = '<!DOCTYPE' in prompt or 'HTML' in prompt.upper()
                
                if es_html:
                    # Configuración OPTIMIZADA para HTML: menos parámetros = más rápido
                    options = {
                        "num_predict": max_tokens,
                        "temperature": temperature,
                        "num_ctx": 4096  # Contexto reducido para velocidad
                    }
                else:
                    # Configuración completa para código complejo
                    options = {
                        "num_predict": max_tokens,
                        "temperature": temperature,
                        "top_p": 0.9,
                        "top_k": 40,
                        "repeat_penalty": 1.1,
                        "presence_penalty": 0.3,
                        "frequency_penalty": 0.3,
                        "num_ctx": 8192
                    }
                
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                    "options": options
                }
            else:
                # Usar endpoint /api/generate para modelos de código
                api_url = f"{self.endpoint}/api/generate"
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature,
                        "top_p": 0.8,
                        "repeat_penalty": 1.1
                    }
                }
            
            response = requests.post(
                api_url,
                json=payload,
                timeout=self.timeout,
            )

            if response.status_code != 200:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")
                return None

            data = response.json()
            
            # Extraer texto según el tipo de endpoint
            if is_chat_model:
                # Endpoint /api/chat devuelve message.content
                text = data.get("message", {}).get("content", "").strip()
            else:
                # Endpoint /api/generate devuelve response
                text = data.get("response", "").strip()

            if not text:
                print("⚠️ Respuesta vacía de Ollama")
                print("🧠 RAW OLLAMA:", data)
                return None

            print(f"✅ Respuesta generada ({len(text)} chars)")
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
