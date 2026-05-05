"""
Script de diagnóstico para verificar que todos los módulos se pueden importar
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_import(module_path, description):
    """Intenta importar un módulo"""
    try:
        __import__(module_path)
        print(f"✅ {description}")
        return True
    except Exception as e:
        print(f"❌ {description}: {e}")
        return False

print("="*70)
print("DIAGNÓSTICO DE IMPORTS")
print("="*70)

results = []

# Core modules
print("\n📦 Módulos Core:")
results.append(test_import('agent.core.brain', 'Brain'))
results.append(test_import('agent.core.state_manager', 'State Manager'))
results.append(test_import('agent.core.orchestrator', 'Orchestrator'))
results.append(test_import('agent.core.logger', 'Logger'))
results.append(test_import('agent.core.conversation_manager', 'Conversation Manager'))
results.append(test_import('agent.core.security', 'Security'))
results.append(test_import('agent.core.cache', 'Cache'))
results.append(test_import('agent.core.retry_engine', 'Retry Engine'))
results.append(test_import('agent.core.project_analyzer', 'Project Analyzer'))
results.append(test_import('agent.core.prompt_security', 'Prompt Security'))
results.append(test_import('agent.core.stability', 'Stability'))

# LLM modules
print("\n🤖 Módulos LLM:")
results.append(test_import('agent.llm.config', 'LLM Config'))
results.append(test_import('agent.llm.providers', 'LLM Providers'))
results.append(test_import('agent.llm.provider_manager', 'Provider Manager'))
results.append(test_import('agent.llm.client', 'LLM Client'))

# Actions/Commands
print("\n⚙️  Módulos Actions/Commands:")
results.append(test_import('agent.actions.commands.base', 'Command Base'))
results.append(test_import('agent.actions.commands.fix_command', 'Fix Command'))
results.append(test_import('agent.actions.commands.setpath_command', 'SetPath Command'))
results.append(test_import('agent.actions.commands.scan_command', 'Scan Command'))
results.append(test_import('agent.actions.commands.chat_command', 'Chat Command'))
results.append(test_import('agent.actions.executor', 'Executor'))
results.append(test_import('agent.actions.strategies', 'Strategies'))

# Web
print("\n🌐 Módulos Web:")
results.append(test_import('web', 'Web App'))

# Legacy
print("\n📜 Módulos Legacy:")
results.append(test_import('agent.analyzer', 'Analyzer'))
results.append(test_import('agent.extractor', 'Extractor'))

# Resumen
print("\n" + "="*70)
passed = sum(results)
total = len(results)
print(f"Resultado: {passed}/{total} imports exitosos")
print("="*70)

if passed == total:
    print("\n✅ Todos los módulos se importan correctamente")
    sys.exit(0)
else:
    print(f"\n⚠️  {total - passed} módulo(s) tienen problemas de import")
    sys.exit(1)
