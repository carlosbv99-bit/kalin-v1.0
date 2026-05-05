from typing import Dict, List
from enum import Enum
import os


class ProviderType(Enum):
    """Tipos de proveedores LLM soportados"""
    OLLAMA = "ollama"
    OLLAMA_CHAT = "ollama_chat"  # Modelo especializado para chat
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    HUGGING_FACE = "huggingface"


class LLMConfig:
    """Configuración centralizada de LLM (LOCAL-FIRST + ESCALABLE)"""

    # =========================
    # MODO GLOBAL
    # =========================
    # local  -> solo Ollama
    # hybrid -> Ollama + fallback cloud
    # cloud  -> solo cloud
    MODE = os.getenv("KALIN_MODE", "local").lower()

    # =========================
    # PROVEEDORES
    # =========================
    PROVIDERS = {
        ProviderType.OLLAMA: {
            "endpoint": os.getenv("OLLAMA_ENDPOINT", "http://127.0.0.1:11434"),
            "model": os.getenv("OLLAMA_MODEL", "deepseek-coder:latest"),
            "api_key": None,
            "timeout": int(os.getenv("OLLAMA_TIMEOUT", 180)),  # 🔥 más margen local
            "cost_per_1k": 0,
        },
        # Modelo especializado para CHAT/CONVERSACIÓN
        ProviderType.OLLAMA_CHAT: {
            "endpoint": os.getenv("OLLAMA_ENDPOINT", "http://127.0.0.1:11434"),
            "model": os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:7b"),  # Modelo conversacional
            "api_key": None,
            "timeout": int(os.getenv("OLLAMA_TIMEOUT", 180)),
            "cost_per_1k": 0,
        },
        ProviderType.OPENAI: {
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "model": os.getenv("OPENAI_MODEL", "gpt-4-turbo"),
            "api_key": os.getenv("OPENAI_API_KEY"),
            "timeout": 30,
            "cost_per_1k": 0.03,
        },
        ProviderType.ANTHROPIC: {
            "endpoint": "https://api.anthropic.com/v1/messages",
            "model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet"),
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "timeout": 30,
            "cost_per_1k": 0.015,
        },
        ProviderType.AZURE: {
            "endpoint": os.getenv("AZURE_ENDPOINT"),
            "model": os.getenv("AZURE_DEPLOYMENT"),
            "api_key": os.getenv("AZURE_API_KEY"),
            "timeout": 30,
            "cost_per_1k": 0.03,
        },
        ProviderType.HUGGING_FACE: {
            # ⚠️ no siempre 100% compatible con OpenAI format
            "endpoint": "https://api-inference.huggingface.co/models",
            "model": os.getenv("HF_MODEL", "meta-llama/Llama-2-7b-chat-hf"),
            "api_key": os.getenv("HF_API_KEY"),
            "timeout": 30,
            "cost_per_1k": 0.001,
        },
    }

    # =========================
    # FALLBACK DINÁMICO
    # =========================
    @classmethod
    def get_fallback_order(cls) -> List[ProviderType]:
        """Orden de fallback según modo"""

        if cls.MODE == "local":
            return [ProviderType.OLLAMA]

        elif cls.MODE == "hybrid":
            return [
                ProviderType.OLLAMA,
                ProviderType.OPENAI,
                ProviderType.ANTHROPIC,
            ]

        elif cls.MODE == "cloud":
            return [
                ProviderType.OPENAI,
                ProviderType.ANTHROPIC,
            ]

        return [ProviderType.OLLAMA]

    # =========================
    # ROUTING POR CASO DE USO
    # =========================
    USE_CASE_ROUTER = {
        "fix": {"max_tokens": 4000},
        "enhance": {"max_tokens": 4000},
        "analyze": {"max_tokens": 1200},
        "create": {"max_tokens": 4000},
        "design": {"max_tokens": 4000},
        "test": {"max_tokens": 2000},
        "doc": {"max_tokens": 2000},
    }

    # =========================
    # HELPERS
    # =========================
    @classmethod
    def get_primary_provider(cls, use_case: str = "fix") -> ProviderType:
        """Siempre prioriza según modo"""

        if cls.MODE == "local":
            return ProviderType.OLLAMA

        elif cls.MODE == "hybrid":
            return ProviderType.OLLAMA

        elif cls.MODE == "cloud":
            return ProviderType.OPENAI

        return ProviderType.OLLAMA

    @classmethod
    def get_max_tokens(cls, use_case: str = "fix") -> int:
        return cls.USE_CASE_ROUTER.get(use_case, {}).get("max_tokens", 1200)

    @classmethod
    def is_configured(cls, provider: ProviderType) -> bool:
        config = cls.PROVIDERS.get(provider)

        if not config:
            return False

        # Ollama y Ollama Chat siempre disponibles en local
        if provider in [ProviderType.OLLAMA, ProviderType.OLLAMA_CHAT]:
            return True

        return bool(config.get("api_key"))

    @classmethod
    def get_available_providers(cls) -> List[ProviderType]:
        return [
            p for p in cls.get_fallback_order()
            if cls.is_configured(p)
        ]

    @classmethod
    def get_provider_config(cls, provider: ProviderType) -> Dict:
        return cls.PROVIDERS.get(provider, {})

    @classmethod
    def get_env_summary(cls) -> Dict:
        return {
            "mode": cls.MODE,
            "available_providers": [p.value for p in cls.get_available_providers()],
            "primary_provider": cls.get_primary_provider().value,
            "fallback_order": [p.value for p in cls.get_fallback_order()],
            "ollama_configured": True,
            "openai_configured": cls.is_configured(ProviderType.OPENAI),
            "anthropic_configured": cls.is_configured(ProviderType.ANTHROPIC),
        }