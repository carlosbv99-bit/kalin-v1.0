"""
Interfaz abstracta para proveedores LLM.

Todos los proveedores (Ollama, OpenAI, Claude, etc.) implementan esta interfaz.
Permite swap entre providers sin cambiar código.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Respuesta estándar de cualquier LLM"""
    text: str
    provider: str
    model: str
    tokens_used: int = 0
    cost: float = 0.0


class BaseLLMProvider(ABC):
    """Clase base para todos los proveedores LLM"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = self.__class__.__name__
        self.model = config.get("model", "unknown")
        self.endpoint = config.get("endpoint")
        self.api_key = config.get("api_key")
        self.timeout = config.get("timeout", 30)

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica si el proveedor está disponible (conectado, credenciales OK)"""
        pass

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 1200) -> Optional[LLMResponse]:
        """
        Genera respuesta para un prompt.

        Args:
            prompt: Texto a procesar
            max_tokens: Máximo de tokens a generar

        Returns:
            LLMResponse con la respuesta, o None si falla
        """
        pass

    def validate_config(self) -> bool:
        """Valida que la configuración sea correcta"""
        if not self.endpoint:
            return False
        return True
