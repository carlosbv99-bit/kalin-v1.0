"""
Configuración de LLM: Proveedores, modelos, costos.

SOPORTADO:
- Ollama (local, gratis)
- OpenAI (GPT-4, GPT-3.5, cloud)
- Anthropic (Claude, cloud)
- Azure (OpenAI en Azure)
- Hugging Face (modelos open-source, cloud)

ESCALABILIDAD:
- Local dev: Ollama gratis
- Producción: OpenAI/Claude
- Fallback automático entre proveedores
"""

from typing import Dict, List
from enum import Enum
import os

class ProviderType(Enum):
    """Tipos de proveedores LLM soportados"""
    OLLAMA = "ollama"          # Local
    OPENAI = "openai"          # Cloud (ChatGPT)
    ANTHROPIC = "anthropic"    # Cloud (Claude)
    AZURE = "azure"            # Cloud (OpenAI en Azure)
    HUGGING_FACE = "huggingface"  # Cloud (open-source)

class LLMConfig:
    """Configuración centralizada de LLM"""

    # Proveedores y endpoints
    PROVIDERS = {
        ProviderType.OLLAMA: {
            "endpoint": os.getenv("OLLAMA_ENDPOINT", "http://127.0.0.1:11434"),
            "model": os.getenv("OLLAMA_MODEL", "deepseek-coder"),
            "api_key": None,  # Ollama no requiere key
            "timeout": 30,
            "cost_per_1k": 0,  # Gratis (local)
        },
        ProviderType.OPENAI: {
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "model": os.getenv("OPENAI_MODEL", "gpt-4-turbo"),
            "api_key": os.getenv("OPENAI_API_KEY"),
            "timeout": 30,
            "cost_per_1k": 0.03,  # $0.03 por 1K tokens
        },
        ProviderType.ANTHROPIC: {
            "endpoint": "https://api.anthropic.com/v1/messages",
            "model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet"),
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "timeout": 30,
            "cost_per_1k": 0.015,  # $0.015 por 1K tokens
        },
        ProviderType.AZURE: {
            "endpoint": os.getenv("AZURE_ENDPOINT"),
            "model": os.getenv("AZURE_DEPLOYMENT"),
            "api_key": os.getenv("AZURE_API_KEY"),
            "timeout": 30,
            "cost_per_1k": 0.03,
        },
        ProviderType.HUGGING_FACE: {
            "endpoint": "https://api-inference.huggingface.co/v1/chat/completions",
            "model": os.getenv("HF_MODEL", "meta-llama/Llama-2-7b-chat-hf"),
            "api_key": os.getenv("HF_API_KEY"),
            "timeout": 30,
            "cost_per_1k": 0.001,  # Muy barato
        },
    }

    # Orden de fallback (si falla primero, intenta siguiente)
    FALLBACK_ORDER = [
        ProviderType.OPENAI,
        ProviderType.ANTHROPIC,
        ProviderType.OLLAMA,
        ProviderType.HUGGING_FACE,
    ]

    # Casos de uso específicos: qué modelo usar para cada tarea
    USE_CASE_ROUTER = {
        "fix": {
            "primary": ProviderType.OPENAI,      # GPT-4 mejor para análisis
            "fallback": [ProviderType.ANTHROPIC, ProviderType.OLLAMA],
            "max_tokens": 1500,
        },
        "enhance": {
            "primary": ProviderType.OPENAI,
            "fallback": [ProviderType.ANTHROPIC, ProviderType.OLLAMA],
            "max_tokens": 1500,
        },
        "analyze": {
            "primary": ProviderType.OPENAI,
            "fallback": [ProviderType.ANTHROPIC, ProviderType.OLLAMA],
            "max_tokens": 500,
        },
        "create": {
            "primary": ProviderType.OPENAI,      # GPT-4 mejor para generar
            "fallback": [ProviderType.ANTHROPIC, ProviderType.OLLAMA],
            "max_tokens": 2000,
        },
        "design": {
            "primary": ProviderType.OPENAI,
            "fallback": [ProviderType.ANTHROPIC],
            "max_tokens": 3000,
        },
        "test": {
            "primary": ProviderType.HUGGING_FACE,  # Barato para tests
            "fallback": [ProviderType.OPENAI, ProviderType.ANTHROPIC],
            "max_tokens": 2000,
        },
        "doc": {
            "primary": ProviderType.HUGGING_FACE,  # Barato para docs
            "fallback": [ProviderType.OPENAI],
            "max_tokens": 1500,
        },
    }

    # Modo de ejecución
    MODE = os.getenv("AGENTE_MODE", "local")  # "local" o "cloud"

    @classmethod
    def get_primary_provider(cls, use_case: str = "fix") -> ProviderType:
        """Obtiene proveedor primario para un caso de uso"""
        if use_case in cls.USE_CASE_ROUTER:
            return cls.USE_CASE_ROUTER[use_case]["primary"]
        return ProviderType.OPENAI  # Default

    @classmethod
    def get_max_tokens(cls, use_case: str = "fix") -> int:
        """Obtiene max tokens para un caso de uso"""
        if use_case in cls.USE_CASE_ROUTER:
            return cls.USE_CASE_ROUTER[use_case]["max_tokens"]
        return 1200  # Default

    @classmethod
    def is_configured(cls, provider: ProviderType) -> bool:
        """Verifica si un proveedor está configurado (tiene key/endpoint)"""
        config = cls.PROVIDERS.get(provider)
        if not config:
            return False

        # Ollama no necesita API key
        if provider == ProviderType.OLLAMA:
            return True

        # Otros proveedores necesitan API key
        return bool(config.get("api_key"))

    @classmethod
    def get_available_providers(cls) -> List[ProviderType]:
        """Retorna lista de proveedores disponibles (configurados)"""
        return [p for p in cls.PROVIDERS.keys() if cls.is_configured(p)]

    @classmethod
    def get_env_summary(cls) -> Dict:
        """Debug: muestra qué está configurado"""
        return {
            "mode": cls.MODE,
            "available_providers": [p.value for p in cls.get_available_providers()],
            "primary_provider": cls.get_primary_provider().value,
            "fallback_order": [p.value for p in cls.FALLBACK_ORDER],
            "ollama_configured": cls.is_configured(ProviderType.OLLAMA),
            "openai_configured": cls.is_configured(ProviderType.OPENAI),
            "anthropic_configured": cls.is_configured(ProviderType.ANTHROPIC),
        }
