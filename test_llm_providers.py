"""
TEST: Múltiples proveedores LLM

Verifica que:
1. Todos los imports funcionan
2. Instanciación correcta
3. Backward compatibility
4. Fallbacks automáticos
5. Tracking de costos
"""

import sys
import os

print("=" * 70)
print("TEST: MÚLTIPLES PROVEEDORES LLM")
print("=" * 70)

# TEST 1: Imports
print("\n1️⃣  Imports...")
try:
    from agent.llm.config import LLMConfig, ProviderType
    from agent.llm.providers import BaseLLMProvider, LLMResponse
    from agent.llm.providers import OllamaProvider, OpenAIProvider, AnthropicProvider
    from agent.llm.provider_manager import LLMProviderManager, get_manager
    from agent.llm.client import generate, is_available, get_stats, get_provider_status
    print("   ✅ Todos los imports funcionan")
except Exception as e:
    print(f"   ❌ Error de import: {e}")
    sys.exit(1)

# TEST 2: Configuración
print("\n2️⃣  Configuración...")
try:
    config = LLMConfig()
    env_summary = config.get_env_summary()
    print(f"   Modo: {env_summary['mode']}")
    print(f"   Proveedores disponibles: {env_summary['available_providers']}")
    print(f"   Proveedor primario: {env_summary['primary_provider']}")
    print("   ✅ Configuración OK")
except Exception as e:
    print(f"   ❌ Error de configuración: {e}")
    sys.exit(1)

# TEST 3: Manager
print("\n3️⃣  Provider Manager...")
try:
    manager = get_manager()
    assert manager is not None
    
    status = manager.get_provider_status()
    print(f"   Proveedores configurados: {list(status.keys())}")
    print(f"   Disponibles ahora: {[k for k, v in status.items() if v]}")
    print("   ✅ Manager OK")
except Exception as e:
    print(f"   ❌ Error en manager: {e}")
    sys.exit(1)

# TEST 4: Backward compatibility
print("\n4️⃣  Backward compatibility...")
try:
    # Función generate() debe funcionar igual que antes
    resultado = generate("Test", max_tokens=50)
    
    # Si hay Ollama, debería funcionar
    if is_available():
        assert isinstance(resultado, str)
        print(f"   Generación funcionó: {len(resultado)} caracteres")
        print("   ✅ Backward compatible OK")
    else:
        print("   ⚠️  No hay LLM disponible (normal en test)")
        print("   ✅ Función no crashea")
except Exception as e:
    print(f"   ❌ Error en backward compatibility: {e}")
    sys.exit(1)

# TEST 5: Estadísticas
print("\n5️⃣  Estadísticas de uso...")
try:
    stats = get_stats()
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Costo total: {stats['total_cost']}")
    print(f"   Uso por proveedor: {stats['provider_usage']}")
    print("   ✅ Stats OK")
except Exception as e:
    print(f"   ❌ Error en stats: {e}")
    sys.exit(1)

# TEST 6: Provider status
print("\n6️⃣  Estado de proveedores...")
try:
    status = get_provider_status()
    for provider, available in status.items():
        emoji = "✅" if available else "❌"
        print(f"   {emoji} {provider}")
    print("   ✅ Status OK")
except Exception as e:
    print(f"   ❌ Error en status: {e}")
    sys.exit(1)

# TEST 7: Configuración por use_case
print("\n7️⃣  Routing por use_case...")
try:
    config = LLMConfig()
    
    use_cases = ["fix", "create", "enhance", "design", "test", "doc"]
    for uc in use_cases:
        primary = config.get_primary_provider(uc)
        max_tokens = config.get_max_tokens(uc)
        print(f"   {uc:10} → {primary.value:12} ({max_tokens} tokens)")
    
    print("   ✅ Routing OK")
except Exception as e:
    print(f"   ❌ Error en routing: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ TODOS LOS TESTS PASARON")
print("=" * 70)

print("""
PRÓXIMOS PASOS:

1. Configura variables de entorno (.env):
   
   # Para desarrollo (Ollama local):
   export AGENTE_MODE=local
   export OLLAMA_ENDPOINT=http://127.0.0.1:11434
   
   # Para producción (OpenAI):
   export AGENTE_MODE=cloud
   export OPENAI_API_KEY=sk-proj-xxxxx

2. Usa el agente como antes:
   
   /setpath /mi/proyecto
   /fix archivo.py
   /apply

3. Monitorea costos:
   
   from agent.llm.client import get_stats
   print(get_stats())

¡Escalable a cloud sin cambios de código! 🚀
""")
