from typing import Dict, List
from enum import Enum
import os


class ProviderType(Enum):
    """Tipos de proveedores LLM soportados"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    HUGGING_FACE = "huggingface"
    GROQ = "groq"
    GEMINI = "gemini"
    MISTRAL = "mistral"
    MIMO = "mimo"


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
        ProviderType.GROQ: {
            "endpoint": "https://api.groq.com/openai/v1",
            "model": os.getenv("GROQ_MODEL", os.getenv("GROK_MODEL", "llama-3.1-8b-instant")),
            "api_key": os.getenv("GROQ_API_KEY", os.getenv("GROK_API_KEY")),
            "timeout": 30,
            "cost_per_1k": 0,  # Gratis actualmente
        },
        ProviderType.GEMINI: {
            "endpoint": "https://generativelanguage.googleapis.com",
            "model": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            "api_key": os.getenv("GEMINI_API_KEY"),
            "timeout": 30,
            "cost_per_1k": 0,  # Gratis con límites
        },
        ProviderType.MISTRAL: {
            "endpoint": "https://api.mistral.ai/v1",
            "model": os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
            "api_key": os.getenv("MISTRAL_API_KEY"),
            "timeout": 30,
            "cost_per_1k": 0.002,  # Muy económico
        },
        ProviderType.MIMO: {
            "endpoint": os.getenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1"),
            "model": os.getenv("MIMO_MODEL", "mimo-v2-flash"),
            "api_key": os.getenv("MIMO_API_KEY"),
            "timeout": 60,  # Aumentado para mejor rendimiento
            "cost_per_1k": 0,  # Gratuito temporalmente
        },
    }

    # =========================
    # FALLBACK DINÁMICO
    # =========================
    @classmethod
    def get_fallback_order(cls) -> List[ProviderType]:
        """Orden de fallback según modo y proveedor activo"""
        active = os.getenv("ACTIVE_PROVIDER", "").lower()
        
        # Normalizar 'grok' a 'groq'
        if active in ['grok', 'groq']:
            return [ProviderType.GROQ] # Sin fallback a Ollama para depuración
        elif active == "openai":
            return [ProviderType.OPENAI, ProviderType.OLLAMA]
        elif active == "anthropic":
            return [ProviderType.ANTHROPIC, ProviderType.OLLAMA]

        # Lógica por defecto según el modo
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
        "fix": {"max_tokens": 4000, "temperature": 0.2},      # Backend: código preciso
        "enhance": {"max_tokens": 4000, "temperature": 0.2},   # Backend: código preciso
        "analyze": {"max_tokens": 1200, "temperature": 0.3},   # Backend: análisis técnico
        "create": {"max_tokens": 8000, "temperature": 0.2},    # Backend: generación código (aumentado para webs completas)
        "design": {"max_tokens": 8000, "temperature": 0.3},    # Backend: diseño técnico (aumentado)
        "test": {"max_tokens": 2000, "temperature": 0.2},      # Backend: tests precisos
        "doc": {"max_tokens": 2000, "temperature": 0.3},       # Backend: documentación
        "chat": {"max_tokens": 1000, "temperature": 0.8},      # Frontend: conversacional creativo
        "greeting": {"max_tokens": 500, "temperature": 0.9},   # Frontend: saludos variados
        "show_code": {"max_tokens": 500, "temperature": 0.1},  # Frontend: mostrar código (determinista)
    }

    # =========================
    # HELPERS
    # =========================
    @classmethod
    def get_primary_provider(cls, use_case: str = "fix") -> ProviderType:
        """Prioriza el proveedor activo configurado por el usuario"""
        
        # 1. Verificar si hay un proveedor activo explícito en .env
        active = os.getenv("ACTIVE_PROVIDER", "").lower()
        # Normalizar 'grok' a 'groq'
        if active in ['grok', 'groq']:
            return ProviderType.GROQ # Usamos Groq como proxy para xAI/Grok
        elif active == "openai":
            return ProviderType.OPENAI
        elif active == "anthropic":
            return ProviderType.ANTHROPIC
        elif active == "ollama":
            return ProviderType.OLLAMA
        elif active == "mimo":
            return ProviderType.MIMO

        # 2. Si no hay activo, usar la lógica por defecto según el modo
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
    def get_temperature(cls, use_case: str = "fix") -> float:
        """Obtiene temperatura configurada para el caso de uso"""
        return cls.USE_CASE_ROUTER.get(use_case, {}).get("temperature", 0.7)

    @classmethod
    def is_configured(cls, provider: ProviderType) -> bool:
        config = cls.PROVIDERS.get(provider)

        if not config:
            return False

        # Ollama siempre disponible en local
        if provider == ProviderType.OLLAMA:
            return True

        return bool(config.get("api_key"))

    @classmethod
    def get_available_providers(cls) -> List[ProviderType]:
        return [
            p for p in cls.get_fallback_order()
            if cls.is_configured(p)
        ]
    
    @classmethod
    def get_configured_cloud_providers(cls) -> List[Dict[str, str]]:
        """
        Obtiene dinámicamente todos los proveedores de nube configurados.
        Retorna lista de dicts con: provider_type, model_name, display_name
        """
        # Recargar .env para obtener configuraciones actualizadas
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        configured = []
        
        # Mapeo de nombres amigables para mostrar
        provider_display_names = {
            'openai': 'OpenAI',
            'anthropic': 'Anthropic',
            'azure': 'Azure',
            'huggingface': 'HuggingFace',
            'groq': 'Groq',
            'gemini': 'Gemini',
            'mistral': 'Mistral',
            'mimo': 'MiMo',
        }
        
        for provider_type, config in cls.PROVIDERS.items():
            # Saltar Ollama (es local)
            if provider_type == ProviderType.OLLAMA:
                continue
            
            # Verificar si está configurado (tiene API key)
            # IMPORTANTE: Re-verificar usando os.getenv directamente para datos actualizados
            if provider_type == ProviderType.OPENAI:
                is_config = bool(os.getenv("OPENAI_API_KEY"))
            elif provider_type == ProviderType.ANTHROPIC:
                is_config = bool(os.getenv("ANTHROPIC_API_KEY"))
            elif provider_type == ProviderType.AZURE:
                is_config = bool(os.getenv("AZURE_API_KEY"))
            elif provider_type == ProviderType.HUGGING_FACE:
                is_config = bool(os.getenv("HF_API_KEY"))
            elif provider_type == ProviderType.GROQ:
                is_config = bool(os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY"))
            elif provider_type == ProviderType.GEMINI:
                is_config = bool(os.getenv("GEMINI_API_KEY"))
            elif provider_type == ProviderType.MISTRAL:
                is_config = bool(os.getenv("MISTRAL_API_KEY"))
            elif provider_type == ProviderType.MIMO:
                is_config = bool(os.getenv("MIMO_API_KEY"))
            else:
                is_config = False
            
            if is_config:
                # Obtener el modelo actualizado directamente del environment
                if provider_type == ProviderType.OPENAI:
                    model_name = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
                elif provider_type == ProviderType.ANTHROPIC:
                    model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet")
                elif provider_type == ProviderType.AZURE:
                    model_name = os.getenv("AZURE_DEPLOYMENT", "unknown")
                elif provider_type == ProviderType.HUGGING_FACE:
                    model_name = os.getenv("HF_MODEL", "meta-llama/Llama-2-7b-chat-hf")
                elif provider_type == ProviderType.GROQ:
                    model_name = os.getenv("GROQ_MODEL", os.getenv("GROK_MODEL", "llama-3.1-8b-instant"))
                elif provider_type == ProviderType.GEMINI:
                    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
                elif provider_type == ProviderType.MISTRAL:
                    model_name = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
                elif provider_type == ProviderType.MIMO:
                    model_name = os.getenv("MIMO_MODEL", "mimo-v2-flash")
                else:
                    model_name = 'unknown'
                    
                provider_value = provider_type.value
                display_name = provider_display_names.get(provider_value, provider_value.title())
                
                configured.append({
                    'provider_type': provider_value,
                    'model_name': model_name,
                    'display_name': f"{model_name} (Nube - {display_name})"
                })
        
        return configured

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