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

    def __init__(self, config=None):
        super().__init__(config)
        self._available_models = []
        self._last_refresh = 0
        # Aumentar timeout para modelos locales (pueden ser lentos)
        if not config or 'timeout' not in config:
            self.timeout = 120  # 2 minutos para Ollama

    def refresh_models(self):
        """Refresca la lista de modelos disponibles en Ollama"""
        import time
        try:
            response = requests.get(f"{self.endpoint}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                self._available_models = models
                self._last_refresh = time.time()
                print(f"✅ Modelos Ollama actualizados: {len(models)} modelos encontrados")
                return models
        except Exception as e:
            print(f"⚠️ Error refrescando modelos: {e}")
        return self._available_models

    def get_available_models(self):
        """Obtiene lista de modelos disponibles (con cache de 30 segundos)"""
        import time
        # Refrescar si pasaron más de 30 segundos o si está vacío
        if not self._available_models or (time.time() - self._last_refresh) > 30:
            return self.refresh_models()
        return self._available_models

    def is_model_available(self, model_name: str) -> bool:
        """Verifica si un modelo específico está disponible"""
        models = self.get_available_models()
        # Verificar coincidencia exacta o parcial
        return any(model_name in m or m in model_name for m in models)

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
            # IMPORTANTE: Leer modelo actualizado del environment cada vez
            import os
            current_model = os.getenv('OLLAMA_MODEL', self.model)
            
            # Detectar si es modelo de chat y usar endpoint apropiado
            is_chat_model = "chat" in current_model or "qwen" in current_model.lower() or "llama" in current_model.lower()
            
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
                    "model": current_model,  # USAR MODELO ACTUAL DEL ENVIRONMENT
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
                    "model": current_model,  # USAR MODELO ACTUAL DEL ENVIRONMENT
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

            print(f"✅ Respuesta generada ({len(text)} chars) con modelo: {current_model}")
            return LLMResponse(
                text=text,
                provider="ollama",
                model=current_model,
                tokens_used=data.get("eval_count", 0),
                cost=0.0  # Ollama es gratis (local)
            )

        except Exception as e:
            print(f"❌ Ollama error: {e}")
            return None
