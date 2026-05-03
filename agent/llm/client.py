"""
LLM Client - Interfaz unificada.

Soporta múltiples proveedores con fallbacks automáticos.
API BACKWARD COMPATIBLE: generate() y is_available() trabajan igual.

Cambios internos:
- Local (dev): Ollama (gratis)
- Cloud (prod): OpenAI → Claude → Ollama
"""

from agent.llm.provider_manager import get_manager

# Para backward compatibility con código existente
_manager = None

def _get_manager():
    global _manager
    if _manager is None:
        _manager = get_manager()
    return _manager

def generate(prompt: str, max_tokens: int = 300, use_case: str = "fix") -> str:
    """
    Genera respuesta usando proveedores inteligentes.

    BACKWARD COMPATIBLE: API igual a antes.

    Args:
        prompt: Texto a procesar
        max_tokens: Máximo de tokens
        use_case: "fix", "create", "enhance", etc. (nuevo, pero opcional)

    Returns:
        Texto generado (vacío si falla todo)
    """
    manager = _get_manager()
    response = manager.generate(prompt, use_case=use_case, max_tokens=max_tokens)

    if response:
        return response.text
    return ""

def is_available() -> bool:
    """
    Verifica si hay algún proveedor disponible.

    BACKWARD COMPATIBLE: API igual a antes.

    Returns:
        True si al menos uno está disponible
    """
    manager = _get_manager()
    status = manager.get_provider_status()
    return any(status.values())

def get_stats():
    """NUEVO: Retorna estadísticas de uso"""
    manager = _get_manager()
    return manager.get_stats()

def get_provider_status():
    """NUEVO: Retorna estado de cada proveedor"""
    manager = _get_manager()
    return manager.get_provider_status()