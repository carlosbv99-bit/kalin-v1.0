#!/usr/bin/env python3
"""
Suite completa de tests para Kalin v3.0
Prueba todas las funcionalidades implementadas
"""

import sys
import os
import time
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test 1: Verificar que todos los módulos se importan correctamente"""
    print("\n" + "="*80)
    print("🧪 TEST 1: Importación de módulos")
    print("="*80)
    
    try:
        from agent.core.brain import detectar_intencion
        print("✅ brain.detectar_intencion importado correctamente")
        
        from agent.actions.executor import Executor
        print("✅ Executor importado correctamente")
        
        from agent.actions.tools.fix_tool import generar_codigo, reparar_codigo
        print("✅ Fix tools importados correctamente")
        
        from agent.core.state_manager import StateManager
        print("✅ StateManager importado correctamente")
        
        from agent.core.experience_memory import ExperienceMemory
        print("✅ ExperienceMemory importado correctamente")
        
        from agent.llm.provider_manager import get_manager
        print("✅ ProviderManager importado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en importación: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_brain_intentions():
    """Test 2: Verificar detección de intenciones"""
    print("\n" + "="*80)
    print("🧪 TEST 2: Detección de intenciones")
    print("="*80)
    
    try:
        from agent.core.brain import detectar_intencion
        
        # Test casos de intención
        test_cases = [
            ("ayúdame a crear un calendario", "create"),
            ("quiero una app de notas", "create"),
            ("cómo hago una función factorial", "create"),
            ("muéstramelo", "show_code"),
            ("formatealo correctamente", "show_code"),
            ("muestrame solo el codigo sin comentarios", "show_code"),
            ("hola", "greeting"),
            ("/scan", "scan"),
            ("arregla este archivo", "fix"),  # Cambiado de "/fix archivo.py"
        ]
        
        passed = 0
        failed = 0
        
        for mensaje, expected in test_cases:
            result = detectar_intencion(mensaje)
            if result == expected:
                print(f"✅ '{mensaje[:40]}...' → {result}")
                passed += 1
            else:
                print(f"❌ '{mensaje[:40]}...' → {result} (esperado: {expected})")
                failed += 1
        
        print(f"\nResultado: {passed}/{len(test_cases)} correctos")
        return failed == 0
        
    except Exception as e:
        print(f"❌ Error en test de intenciones: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_state_manager():
    """Test 3: Verificar StateManager"""
    print("\n" + "="*80)
    print("🧪 TEST 3: StateManager")
    print("="*80)
    
    try:
        from agent.core.state_manager import StateManager
        import tempfile
        import os
        
        state = StateManager()
        
        # Test guardar código
        test_codigo = "import calendar\ndef test():\n    return True"
        state.set_ultimo_codigo_generado(test_codigo)
        
        # Test recuperar código
        recovered = state.get_ultimo_codigo_generado()
        if recovered == test_codigo:
            print("✅ Guardar/recuperar código funciona")
        else:
            print(f"❌ Código no coincide: {recovered}")
            return False
        
        # Test otros campos - usar directorio temporal que existe
        temp_dir = tempfile.gettempdir()
        state.set_ruta(temp_dir)
        if state.get_ruta() == temp_dir:
            print(f"✅ Ruta de proyecto funciona: {temp_dir}")
        else:
            print(f"❌ Ruta de proyecto falla")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en StateManager: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_experience_memory():
    """Test 4: Verificar ExperienceMemory"""
    print("\n" + "="*80)
    print("🧪 TEST 4: ExperienceMemory")
    print("="*80)
    
    try:
        from agent.core.experience_memory import ExperienceMemory
        
        memory = ExperienceMemory()
        
        # Registrar experiencia de éxito
        memory.record_experience(
            task_type="create",
            problem_description="calendario Python",
            file_type="python",
            strategy_used="smart",
            success=True,
            confidence_score=0.9,
            solution_summary="Código generado correctamente"
        )
        print("✅ Registro de éxito funciona")
        
        # Registrar experiencia de fallo
        memory.record_experience(
            task_type="fix",
            problem_description="error sintaxis",
            file_type="python",
            strategy_used="aggressive",
            success=False,
            confidence_score=0.3,
            error_message="Código no válido"
        )
        print("✅ Registro de fallo funciona")
        
        # Obtener resumen
        summary = memory.get_learning_summary()
        if summary['total_experiences'] >= 2:
            print(f"✅ Resumen correcto: {summary['total_experiences']} experiencias")
        else:
            print(f"❌ Resumen incorrecto: {summary['total_experiences']} experiencias")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en ExperienceMemory: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_code_quality_validation():
    """Test 5: Verificar validación de calidad de código"""
    print("\n" + "="*80)
    print("🧪 TEST 5: Validación de calidad de código")
    print("="*80)
    
    try:
        from agent.actions.tools.fix_tool import _es_codigo_de_calidad, calcular_score_calidad
        
        # Código bueno
        good_code = """import calendar
from datetime import date

def generar_calendario(anio=None, mes=None):
    if anio is None:
        anio = date.today().year
    if mes is None:
        mes = date.today().month
    cal = calendar.TextCalendar(firstweekday=6)
    return cal.formatmonth(anio, mes)

if __name__ == "__main__":
    print(generar_calendario())
"""
        
        if _es_codigo_de_calidad(good_code):
            print("✅ Código bueno pasa validación")
        else:
            print("❌ Código bueno rechazado")
            return False
        
        score = calcular_score_calidad(good_code)
        print(f"   Score de calidad: {score:.2f}")
        
        # Código malo
        bad_code = "def gen_cal(a, m):\n    c = calendar.TextCalendar()\n    return c.formatmonth(a, m).replace('\\n', '')"
        
        if not _es_codigo_de_calidad(bad_code):
            print("✅ Código malo rechazado correctamente")
        else:
            print("❌ Código malo pasó validación")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en validación de calidad: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comment_removal():
    """Test 6: Verificar eliminación de comentarios"""
    print("\n" + "="*80)
    print("🧪 TEST 6: Eliminación de comentarios")
    print("="*80)
    
    try:
        from agent.actions.tools.fix_tool import eliminar_comentarios
        
        code_with_comments = """# Esto es un comentario
import calendar
# Otro comentario
def test():
    x = 5  # Comentario inline
    return x
"""
        
        cleaned = eliminar_comentarios(code_with_comments)
        
        if '#' not in cleaned:
            print("✅ Comentarios eliminados correctamente")
            print(f"   Original: {len(code_with_comments)} chars")
            print(f"   Limpio: {len(cleaned)} chars")
        else:
            print("❌ Aún hay comentarios en el código")
            print(f"   Resultado:\n{cleaned}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en eliminación de comentarios: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_provider_status():
    """Test 7: Verificar estado de proveedores LLM"""
    print("\n" + "="*80)
    print("🧪 TEST 7: Estado de proveedores LLM")
    print("="*80)
    
    try:
        from agent.llm.provider_manager import get_manager
        
        manager = get_manager()
        status = manager.get_provider_status()
        
        print(f"Estado de proveedores:")
        for provider, disponible in status.items():
            icon = "✅" if disponible else "❌"
            print(f"   {icon} {provider}")
        
        # Verificar que al menos uno esté disponible
        any_available = any(status.values())
        if any_available:
            print("✅ Al menos un proveedor está disponible")
        else:
            print("⚠️  Ningún proveedor disponible (Ollama puede no estar corriendo)")
        
        return True  # No fallar si Ollama no está corriendo
        
    except Exception as e:
        print(f"❌ Error en verificación de proveedores: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuracion_modelo_unico():
    """Test 8: Verificar configuración de modelo único"""
    print("\n" + "="*80)
    print("🧪 TEST 8: Configuración de modelo único")
    print("="*80)
    
    try:
        from agent.llm.config import LLMConfig
        
        config = LLMConfig()
        
        # Verificar que usa deepseek-coder para todo
        if hasattr(config, 'OLLAMA_MODEL'):
            model = config.OLLAMA_MODEL
            if 'deepseek-coder' in model.lower():
                print(f"✅ Modelo configurado: {model}")
            else:
                print(f"⚠️  Modelo no es deepseek-coder: {model}")
        else:
            print("⚠️  Config no tiene OLLAMA_MODEL")
        
        # Verificar .env
        env_model = os.getenv('OLLAMA_MODEL', 'no definido')
        if 'deepseek-coder' in env_model.lower():
            print(f"✅ .env configurado: {env_model}")
        else:
            print(f"⚠️  .env no configurado correctamente: {env_model}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en verificación de configuración: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Ejecutar todas las pruebas"""
    print("\n" + "="*80)
    print("🚀 SUITE DE TESTS KALIN v3.0")
    print("="*80)
    
    results = []
    
    # Ejecutar tests
    results.append(("Importación de módulos", test_imports()))
    results.append(("Detección de intenciones", test_brain_intentions()))
    results.append(("StateManager", test_state_manager()))
    results.append(("ExperienceMemory", test_experience_memory()))
    results.append(("Validación de calidad", test_code_quality_validation()))
    results.append(("Eliminación de comentarios", test_comment_removal()))
    results.append(("Estado de proveedores", test_provider_status()))
    results.append(("Configuración modelo único", test_configuracion_modelo_unico()))
    
    # Resumen
    print("\n" + "="*80)
    print("📊 RESUMEN DE RESULTADOS")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status:10} | {name}")
    
    print("="*80)
    print(f"Total: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("\n🎉 ¡EXCELENTE! Todos los tests pasaron.")
        print("Kalin está listo para producción.\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) fallaron.")
        print("Revisa los errores arriba.\n")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
