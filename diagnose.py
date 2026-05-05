"""
Script de diagnóstico automático del proyecto
Identifica todos los problemas antes de ejecutar tests
"""

import sys
import os
from pathlib import Path

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def check_file_exists(filepath, description):
    """Verifica si un archivo existe"""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_import(module_name, description):
    """Verifica si un módulo se puede importar"""
    try:
        __import__(module_name)
        print(f"✅ {description}")
        return True
    except Exception as e:
        print(f"❌ {description}: {e}")
        return False

def main():
    print_section("DIAGNÓSTICO DEL PROYECTO AGENTE-IA2")
    
    project_root = Path(__file__).parent
    print(f"\n📁 Directorio del proyecto: {project_root}")
    
    # 1. Verificar archivos críticos
    print_section("1. ARCHIVOS CRÍTICOS")
    
    critical_files = [
        ("web.py", "Servidor Flask"),
        ("run.py", "Script de inicio"),
        ("agent/__init__.py", "Paquete agent"),
        ("agent/core/brain.py", "Brain module"),
        ("agent/core/orchestrator.py", "Orchestrator"),
        ("agent/core/state_manager.py", "State Manager"),
        ("agent/actions/executor.py", "Executor"),
        ("agent/llm/client.py", "LLM Client"),
        ("agent/llm/provider_manager.py", "Provider Manager"),
    ]
    
    missing_files = []
    for filepath, desc in critical_files:
        full_path = project_root / filepath
        if not check_file_exists(full_path, desc):
            missing_files.append(filepath)
    
    # 2. Verificar imports
    print_section("2. IMPORTS DE PYTHON")
    
    sys.path.insert(0, str(project_root))
    
    imports_to_check = [
        ("flask", "Flask framework"),
        ("agent.core.brain", "Brain module"),
        ("agent.core.state_manager", "State Manager"),
        ("agent.actions.executor", "Executor"),
        ("agent.llm.client", "LLM Client"),
    ]
    
    failed_imports = []
    for module, desc in imports_to_check:
        if not check_import(module, desc):
            failed_imports.append(module)
    
    # 3. Verificar estructura de directorios
    print_section("3. ESTRUCTURA DE DIRECTORIOS")
    
    required_dirs = [
        "agent",
        "agent/core",
        "agent/llm",
        "agent/actions",
        "agent/templates",
    ]
    
    for dirpath in required_dirs:
        full_path = project_root / dirpath
        exists = full_path.is_dir()
        status = "✅" if exists else "❌"
        print(f"{status} {dirpath}/")
    
    # 4. Verificar configuración
    print_section("4. CONFIGURACIÓN")
    
    env_exists = (project_root / ".env").exists()
    env_example_exists = (project_root / ".env.example").exists()
    
    if env_exists:
        print("✅ Archivo .env configurado")
    elif env_example_exists:
        print("⚠️  Solo existe .env.example (debes crear .env)")
    else:
        print("❌ No hay archivo .env ni .env.example")
    
    # 5. Verificar dependencias instaladas
    print_section("5. DEPENDENCIAS INSTALADAS")
    
    dependencies = [
        "flask",
        "flask_cors",
        "pydantic",
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} (no instalado)")
    
    # 6. Resumen
    print_section("RESUMEN DEL DIAGNÓSTICO")
    
    issues = []
    
    if missing_files:
        issues.append(f"Archivos faltantes: {len(missing_files)}")
    
    if failed_imports:
        issues.append(f"Imports fallidos: {len(failed_imports)}")
    
    if not env_exists:
        issues.append("Archivo .env no configurado")
    
    if issues:
        print(f"\n⚠️  Se encontraron {len(issues)} problema(s):\n")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print("\n💡 Ejecuta 'python install.py' para instalar dependencias")
    else:
        print("\n✅ ¡No se encontraron problemas críticos!")
        print("\n🚀 Puedes ejecutar: python run.py")
    
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
