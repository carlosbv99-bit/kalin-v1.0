"""
Manager de proveedores LLM.
Gestiona múltiples proveedores, fallbacks, routing, costos.
"""

from typing import Optional, List, Dict
from agent.llm.config import LLMConfig, ProviderType
from agent.llm.providers.base_provider import LLMResponse
from agent.llm.providers.ollama_provider import OllamaProvider
from agent.llm.providers.openai_provider import OpenAIProvider
from agent.llm.providers.anthropic_provider import AnthropicProvider


class LLMProviderManager:
    """Manager central de proveedores LLM"""

    def __init__(self):
        self.providers = {}
        self.config = LLMConfig()
        self._initialize_providers()
        self.stats = {
            "total_requests": 0,
            "total_cost": 0.0,
            "provider_usage": {},
            "errors": {}
        }

    def _initialize_providers(self):
        """Inicializa los proveedores disponibles"""
        provider_classes = {
            ProviderType.OLLAMA: OllamaProvider,
            ProviderType.OLLAMA_CHAT: OllamaProvider,  # Usa la misma clase pero diferente modelo
            ProviderType.OPENAI: OpenAIProvider,
            ProviderType.ANTHROPIC: AnthropicProvider,
        }

        for provider_type, ProviderClass in provider_classes.items():
            config = LLMConfig.PROVIDERS[provider_type]
            try:
                self.providers[provider_type] = ProviderClass(config)
            except Exception as e:
                print(f"⚠️ No se pudo inicializar {provider_type.value}: {e}")

    def generate(
        self,
        prompt: str,
        use_case: str = "fix",
        max_tokens: Optional[int] = None
    ) -> Optional[LLMResponse]:
        """
        Genera respuesta usando routing inteligente + fallbacks.

        Estrategia:
        1. Selecciona proveedor según tipo de tarea (chat vs código)
        2. Intenta proveedor primario para el use_case
        3. Si falla: intenta fallbacks en orden
        4. Si todo falla: retorna None

        Args:
            prompt: Texto a procesar
            use_case: "fix", "create", "enhance", "design", "chat", etc.
            max_tokens: Máximo tokens (o usa default del use_case)

        Returns:
            LLMResponse o None si falla todo
        """

        # ROUTING INTELIGENTE: Seleccionar modelo según tipo de tarea
        if use_case in ["chat", "greeting", "help"]:
            # Para conversaciones, usar SOLO modelo especializado en chat
            # NO permitir fallback a modelos de código
            selected_provider = ProviderType.OLLAMA_CHAT
            allow_fallback = False  # CRÍTICO: No hacer fallback para chat
        else:
            # Para código, usar modelo especializado en código
            selected_provider = self.config.get_primary_provider(use_case)
            allow_fallback = True  # Permitir fallback para tareas técnicas

        # Obtén configuración para este use_case
        if use_case not in self.config.USE_CASE_ROUTER:
            use_case = "fix"  # Default

        route = self.config.USE_CASE_ROUTER[use_case]
        
        if allow_fallback:
            # Para código: intentar otros proveedores si falla el principal
            fallback_providers = [
                p for p in self.config.get_fallback_order()
                if p != selected_provider
            ]
        else:
            # Para chat: NO fallback, solo usar OLLAMA_CHAT
            fallback_providers = []

        if max_tokens is None:
            max_tokens = route.get("max_tokens", 1200)

        # Construye lista de proveedores a intentar
        providers_to_try = [selected_provider] + fallback_providers

        self.stats["total_requests"] += 1

        # Intenta cada proveedor
        for provider_type in providers_to_try:
            if provider_type not in self.providers:
                continue

            provider = self.providers[provider_type]

            # Verifica disponibilidad
            if not provider.is_available():
                self._record_error(provider_type, "not_available")
                print(f"⚠️ Provider {provider_type.value} no disponible")
                continue

            # DEBUG: Mostrar qué modelo se está usando
            if use_case in ["chat", "greeting", "help"]:
                print(f"💬 CHAT: Usando {provider_type.value} ({provider.model})")
            else:
                print(f"⚙️ CÓDIGO: Usando {provider_type.value} ({provider.model})")

            # Intenta generar
            try:
                response = provider.generate(prompt, max_tokens)

                if response:
                    # Éxito - registra estadísticas
                    self._record_success(provider_type, response)
                    return response
                else:
                    self._record_error(provider_type, "generation_failed")
                    print(f"❌ {provider_type.value} falló en generar respuesta")

            except Exception as e:
                self._record_error(provider_type, str(e))
                print(f"❌ Error en {provider_type.value}: {e}")
                continue

        # Si llegamos aquí, todos fallaron
        return None

    def _record_success(self, provider_type: ProviderType, response: LLMResponse):
        """Registra una generación exitosa"""
        if provider_type not in self.stats["provider_usage"]:
            self.stats["provider_usage"][provider_type.value] = 0

        self.stats["provider_usage"][provider_type.value] += 1
        self.stats["total_cost"] += response.cost

    def _record_error(self, provider_type: ProviderType, error: str):
        """Registra un error"""
        key = provider_type.value
        if key not in self.stats["errors"]:
            self.stats["errors"][key] = []
        self.stats["errors"][key].append(error)

    def get_stats(self) -> Dict:
        """Retorna estadísticas de uso (para billing/debug)"""
        return {
            "total_requests": self.stats["total_requests"],
            "total_cost": f"${self.stats['total_cost']:.4f}",
            "provider_usage": self.stats["provider_usage"],
            "errors": self.stats["errors"],
            "available_providers": [p.value for p in self.config.get_available_providers()],
        }

    def get_provider_status(self) -> Dict[str, bool]:
        """Retorna estado de cada proveedor"""
        return {
            provider_type.value: provider.is_available()
            for provider_type, provider in self.providers.items()
        }


# Instancia global
_manager = None

def get_manager() -> LLMProviderManager:
    """Obtiene la instancia global del manager"""
    global _manager
    if _manager is None:
        _manager = LLMProviderManager()
    return _manager
