"""
VERIFICACIÓN FINAL - Estado del Sistema Kalin
Este script verifica que todas las reparaciones se hayan aplicado correctamente.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

def check_file_exists(filepath, description):
    """Verifica que un archivo exista"""
    if os.path.exists(filepath):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - Archivo no encontrado")
        return False

def check_file_contains(filepath, text, description):
    """Verifica que un archivo contenga texto específico"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if text in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} - Texto no encontrado")
                return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def check_import(module_path, description):
    """Verifica que un módulo se pueda importar"""
    try:
        __import__(module_path)
        print(f"✅ {description}")
        return True
    except Exception as e:
        print(f"❌ {description} - {e}")
        return False

print("="*70)
print("VERIFICACIÓN FINAL DEL SISTEMA KALIN")
print("="*70)

results = []

# 1. Verificar archivos reparados
print("\n📝 ARCHIVOS REPARADOS:")
results.append(check_file_exists('requirements.txt', 'requirements.txt existe'))
results.append(check_file_contains('requirements.txt', 'flask>=2.3.0', 'Flask en requirements.txt'))
results.append(check_file_contains('requirements.txt', 'flask-cors>=4.0.0', 'Flask-CORS en requirements.txt'))

# 2. Verificar reparaciones en test_funcional.py
print("\n🧪 TEST FUNCIONAL:")
results.append(check_file_contains('test_funcional.py', 'from flask import jsonify', 'jsonify importado en test_funcional'))
results.append(check_file_contains('test_funcional.py', '"jsonify": jsonify', 'jsonify agregado a utils'))
results.append(check_file_contains('test_funcional.py', '"session_id": "test_session"', 'session_id agregado al estado'))

# 3. Verificar reparación en retry_engine.py
print("\n🔄 RETRY ENGINE:")
results.append(check_file_contains('agent/core/retry_engine.py', '# Retorna el código incluso si no hubo modificaciones', 'retry_engine retorna código siempre'))

# 4. Verificar reparación en cache.py
print("\n💾 CACHE:")
results.append(check_file_contains('agent/core/cache.py', 'self.load_from_disk()', 'cache.py usa load_from_disk correcto'))

# 5. Verificar test_endpoints.py tenga verificación de servidor
print("\n🌐 TEST ENDPOINTS:")
results.append(check_file_contains('test_endpoints.py', 'Verificar si el servidor está corriendo', 'Verificación de servidor en test_endpoints'))

# 6. Verificar imports críticos
print("\n📦 IMPORTS CRÍTICOS:")
results.append(check_import('agent.core.brain', 'Brain'))
results.append(check_import('agent.core.state_manager', 'State Manager'))
results.append(check_import('agent.core.orchestrator', 'Orchestrator'))
results.append(check_import('agent.core.logger', 'Logger'))
results.append(check_import('agent.core.security', 'Security'))
results.append(check_import('agent.core.cache', 'Cache'))
results.append(check_import('agent.core.retry_engine', 'Retry Engine'))
results.append(check_import('agent.llm.client', 'LLM Client'))
results.append(check_import('agent.actions.commands.base', 'Command Base'))
results.append(check_import('web', 'Web App'))

# 7. Verificar archivos nuevos
print("\n🆕 ARCHIVOS NUEVOS:")
results.append(check_file_exists('run_all_tests.py', 'Script run_all_tests.py'))
results.append(check_file_exists('diagnose_imports.py', 'Script diagnose_imports.py'))
results.append(check_file_exists('REPARACIONES_TESTS.md', 'Documentación de reparaciones'))

# Resumen
print("\n" + "="*70)
passed = sum(results)
total = len(results)
print(f"RESULTADO: {passed}/{total} verificaciones exitosas")
print("="*70)

if passed == total:
    print("\n🎉 ¡TODAS LAS VERIFICACIONES PASARON!")
    print("\n✅ El sistema está listo para ejecutar tests")
    print("\nPróximos pasos:")
    print("1. pip install -r requirements.txt")
    print("2. python run_all_tests.py")
    print("3. python run.py (para iniciar el servidor)")
    sys.exit(0)
else:
    print(f"\n⚠️  {total - passed} verificación(es) fallaron")
    print("\nRevisa los errores arriba y corrige antes de continuar.")
    sys.exit(1)
