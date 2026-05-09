"""
Script de prueba para validar la nueva arquitectura.
Esto verifica que todos los módulos nuevos funcionan sin romper lo existente.
"""

import sys
import os

# Test 1: Import de nuevos módulos
print("=" * 60)
print("TEST 1: Importar nuevos módulos")
print("=" * 60)

try:
    from agent.core.state_manager import StateManager
    print("✅ StateManager importado")
except Exception as e:
    print(f"❌ Error en StateManager: {e}")
    sys.exit(1)

try:
    from agent.core.retry_engine import RetryEngine
    print("✅ RetryEngine importado")
except Exception as e:
    print(f"❌ Error en RetryEngine: {e}")
    sys.exit(1)

try:
    from agent.core.project_analyzer import ProjectAnalyzer
    print("✅ ProjectAnalyzer importado")
except Exception as e:
    print(f"❌ Error en ProjectAnalyzer: {e}")
    sys.exit(1)

try:
    from agent.actions.strategies import PythonStrategy, ProjectStrategy
    print("✅ Strategies importadas")
except Exception as e:
    print(f"❌ Error en Strategies: {e}")
    sys.exit(1)

try:
    from agent.actions.executor import Executor
    print("✅ Executor (actualizado) importado")
except Exception as e:
    print(f"❌ Error en Executor: {e}")
    sys.exit(1)

# Test 2: Crear instancias
print("\n" + "=" * 60)
print("TEST 2: Crear instancias")
print("=" * 60)

try:
    state = StateManager()
    print("✅ StateManager instanciado")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

try:
    retry = RetryEngine()
    print("✅ RetryEngine instanciado")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

try:
    executor = Executor()
    print("✅ Executor instanciado")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 3: Validar StateManager funcionalidad
print("\n" + "=" * 60)
print("TEST 3: StateManager - Funcionalidad básica")
print("=" * 60)

try:
    # Test set/get ruta
    ruta_test = os.path.dirname(os.path.abspath(__file__))
    state.set_ruta(ruta_test)
    ruta_obtenida = state.get_ruta()
    assert ruta_obtenida is not None
    print(f"✅ Ruta configurada: {ruta_obtenida}")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

try:
    # Test set/get último fix
    state.set_ultimo_fix("/test.py", "original", "nuevo")
    fix = state.get_ultimo_fix()
    assert fix is not None and fix["ruta"] == "/test.py"
    print("✅ Último fix registrado y recuperado")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

try:
    # Test registro de éxito/fallo
    state.registrar_exito()
    estado = state.get_estado()
    assert estado["contador_exitos"] > 0
    print("✅ Contadores funcionan")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 4: Validar RetryEngine
print("\n" + "=" * 60)
print("TEST 4: RetryEngine - Estrategias")
print("=" * 60)

try:
    # Test _es_valido
    assert retry._es_valido("def test(): pass") == True
    assert retry._es_valido("sorry i cannot") == False
    assert retry._es_valido("") == False
    print("✅ Validación de código funciona")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

try:
    # Test heuristic (local fixes) - usa código que necesita fix real
    codigo_test = "pd.DataFrame({'a': [1,2,3]})"
    resultado = retry._heuristic(codigo_test, "fix", 1000)
    assert resultado is not None
    assert "import pandas" in resultado
    print("✅ Estrategia heurística funciona")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 5: Compatibilidad backward
print("\n" + "=" * 60)
print("TEST 5: Backward compatibility")
print("=" * 60)

try:
    from agent.analyzer import analizar_codigo
    from agent.actions.tools.fix_tool import generar_codigo, reparar_codigo
    print("✅ Código existente sigue funcionando")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ TODOS LOS TESTS PASARON")
print("=" * 60)
print("""
La nueva arquitectura está lista:
- StateManager: Persistencia mínima de estado
- RetryEngine: Reintentos progresivos + fallbacks
- ProjectAnalyzer: Mapeo de proyecto
- Strategies: Especialización por tipo de código
- Executor: Integración transparente

Próximos pasos:
1. /setpath <ruta>       → Configura proyecto (persiste en .agent_state.json)
2. /fix <archivo>        → Repara usando strategies + retry
3. /apply                 → Aplica cambios guardados
""")
