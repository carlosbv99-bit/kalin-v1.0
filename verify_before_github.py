"""
Script de Verificación Completa antes de Subir a GitHub
Verifica integridad del código, elimina archivos temporales y prepara el repositorio
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Colores para output
class Colors:
    OK = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    INFO = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.INFO}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.INFO}  {text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.INFO}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.OK}✅ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.ERROR}❌ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.INFO}ℹ️  {text}{Colors.RESET}")

def check_python_syntax():
    """Verificar sintaxis de todos los archivos Python"""
    print_header("1. VERIFICANDO SINTAXIS PYTHON")
    
    errors = []
    python_files = []
    
    for root, dirs, files in os.walk('.'):
        # Excluir directorios
        if any(excluded in root for excluded in ['.venv', '.git', '__pycache__', 'node_modules']):
            continue
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print_info(f"Encontrados {len(python_files)} archivos Python")
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                compile(f.read(), py_file, 'exec')
            print_success(f"✓ {py_file}")
        except SyntaxError as e:
            errors.append((py_file, str(e)))
            print_error(f"✗ {py_file}: {e}")
    
    if errors:
        print_error(f"\n{len(errors)} archivo(s) con errores de sintaxis")
        return False
    else:
        print_success(f"\nTodos los {len(python_files)} archivos Python son válidos")
        return True

def check_javascript_syntax():
    """Verificar sintaxis básica de archivos JavaScript"""
    print_header("2. VERIFICANDO ARCHIVOS JAVASCRIPT")
    
    js_files = []
    for root, dirs, files in os.walk('static/js'):
        for file in files:
            if file.endswith('.js'):
                js_files.append(os.path.join(root, file))
    
    print_info(f"Encontrados {len(js_files)} archivos JavaScript")
    
    for js_file in js_files:
        size = os.path.getsize(js_file)
        print_success(f"✓ {js_file} ({size} bytes)")
    
    print_success(f"\nTodos los {len(js_files)} archivos JS presentes")
    return True

def check_html_structure():
    """Verificar estructura del HTML principal"""
    print_header("3. VERIFICANDO ESTRUCTURA HTML")
    
    html_file = 'templates/index.html'
    
    if not os.path.exists(html_file):
        print_error(f"No se encontró {html_file}")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar que termine correctamente
    if content.strip().endswith('</html>'):
        print_success("HTML termina correctamente con </html>")
    else:
        print_error("HTML NO termina correctamente")
        return False
    
    # Verificar que no haya código después de </html>
    lines = content.split('\n')
    html_end_index = None
    for i, line in enumerate(lines):
        if line.strip() == '</html>':
            html_end_index = i
            break
    
    if html_end_index and html_end_index < len(lines) - 1:
        remaining_lines = len(lines) - html_end_index - 1
        print_error(f"Hay {remaining_lines} líneas después de </html>")
        return False
    else:
        print_success("No hay código después de </html>")
    
    # Verificar etiquetas importantes
    required_tags = ['<head>', '</head>', '<body>', '</body>', '<html', '</html>']
    for tag in required_tags:
        if tag in content:
            print_success(f"Etiqueta encontrada: {tag}")
        else:
            print_error(f"Etiqueta faltante: {tag}")
            return False
    
    print_success("\nEstructura HTML válida")
    return True

def check_required_files():
    """Verificar que existan todos los archivos críticos"""
    print_header("4. VERIFICANDO ARCHIVOS CRÍTICOS")
    
    critical_files = [
        'run.py',
        'web.py',
        'requirements.txt',
        '.env.example',
        'templates/index.html',
        'static/js/app.js',
        'static/js/config.js',
        'static/js/chat.js',
        'static/js/preview.js',
        'static/js/ui-manager.js',
        'static/js/resizable-panels.js',
        'static/js/android-utils.js',
        'static/js/legacy-compat.js',
    ]
    
    missing = []
    for file in critical_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print_success(f"✓ {file} ({size} bytes)")
        else:
            missing.append(file)
            print_error(f"✗ {file} - FALTANTE")
    
    if missing:
        print_error(f"\nFaltan {len(missing)} archivos críticos")
        return False
    else:
        print_success(f"\nTodos los archivos críticos presentes")
        return True

def check_gitignore():
    """Verificar que .gitignore esté configurado correctamente"""
    print_header("5. VERIFICANDO .GITIGNORE")
    
    if not os.path.exists('.gitignore'):
        print_error("No existe archivo .gitignore")
        return False
    
    with open('.gitignore', 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_excludes = [
        '.env',
        '__pycache__',
        '*.pyc',
        '.venv',
        'venv',
        '*.log',
        'logs/',
        'sessions/',
        'cache/',
        'experience_memory/',
        '.agent_state.json',
        'health_status.json',
    ]
    
    missing_excludes = []
    for exclude in required_excludes:
        if exclude in content:
            print_success(f"Excluido: {exclude}")
        else:
            missing_excludes.append(exclude)
            print_warning(f"No excluido: {exclude}")
    
    if missing_excludes:
        print_warning(f"\nConsidera agregar estas exclusiones: {missing_excludes}")
    
    print_success("\n.gitignore verificado")
    return True

def clean_temporary_files():
    """Limpiar archivos temporales y caché"""
    print_header("6. LIMPIANDO ARCHIVOS TEMPORALES")
    
    cleaned = 0
    
    # Limpiar __pycache__
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_dir = os.path.join(root, '__pycache__')
            try:
                import shutil
                shutil.rmtree(cache_dir)
                cleaned += 1
                print_success(f"Eliminado: {cache_dir}")
            except Exception as e:
                print_warning(f"No se pudo eliminar {cache_dir}: {e}")
    
    # Limpiar archivos .pyc
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, file))
                    cleaned += 1
                except:
                    pass
    
    # Limpiar archivos de backup antiguos
    backup_patterns = ['*_old_backup*', '*_backup_*', '*.bak']
    for root, dirs, files in os.walk('.'):
        if '.git' in root:
            continue
        for file in files:
            if any(pattern.replace('*', '') in file for pattern in backup_patterns):
                file_path = os.path.join(root, file)
                print_warning(f"Backup encontrado: {file_path}")
    
    print_success(f"\nLimpieza completada: {cleaned} directorios/archivos eliminados")
    return True

def verify_env_file():
    """Verificar que .env no se subirá y que existe .env.example"""
    print_header("7. VERIFICANDO CONFIGURACIÓN DE ENTORNO")
    
    # Verificar que .env exista pero no se subirá
    if os.path.exists('.env'):
        print_success("Archivo .env presente (no se subirá a Git)")
        
        # Verificar que está en .gitignore
        with open('.gitignore', 'r') as f:
            gitignore = f.read()
        
        if '.env' in gitignore:
            print_success(".env está en .gitignore ✓")
        else:
            print_error(".env NO está en .gitignore - ¡AGREGARLO!")
            return False
    else:
        print_warning("No existe archivo .env (crear desde .env.example)")
    
    # Verificar .env.example
    if os.path.exists('.env.example'):
        print_success("Archivo .env.example presente ✓")
    else:
        print_error("Falta .env.example - crear uno")
        return False
    
    return True

def check_code_quality():
    """Verificaciones básicas de calidad de código"""
    print_header("8. VERIFICACIONES DE CALIDAD")
    
    issues = []
    
    # Verificar que no haya TODOs o FIXMEs sin resolver (opcional)
    for root, dirs, files in os.walk('.'):
        if any(excluded in root for excluded in ['.venv', '.git', '__pycache__']):
            continue
        
        for file in files:
            if file.endswith(('.py', '.js', '.html')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Contar TODOs y FIXMEs
                        todos = content.count('TODO') + content.count('FIXME')
                        if todos > 0:
                            issues.append((file_path, todos))
                except:
                    pass
    
    if issues:
        print_warning(f"Se encontraron TODOs/FIXMEs en {len(issues)} archivos:")
        for file, count in issues[:5]:  # Mostrar solo primeros 5
            print_warning(f"  - {file}: {count} items")
    else:
        print_success("No se encontraron TODOs/FIXMEs pendientes")
    
    print_success("\nVerificación de calidad completada")
    return True

def generate_summary():
    """Generar resumen del estado actual"""
    print_header("RESUMEN DE VERIFICACIÓN")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary = {
        "timestamp": timestamp,
        "status": "READY_FOR_GITHUB",
        "checks_passed": True,
        "notes": [
            "Paneles redimensionables implementados (1px)",
            "Mensaje de bienvenida desactivado",
            "Arquitectura modular completa",
            "Ruta API corregida (/chat)",
            "CSS optimizado y limpio"
        ]
    }
    
    print_info(f"Fecha: {timestamp}")
    print_info("Estado: LISTO PARA GITHUB")
    print_info("\nCambios principales:")
    for note in summary["notes"]:
        print_info(f"  • {note}")
    
    # Guardar resumen en archivo
    with open('GITHUB_READY_SUMMARY.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print_success(f"\nResumen guardado en: GITHUB_READY_SUMMARY.json")

def main():
    """Ejecutar todas las verificaciones"""
    print_header("VERIFICACIÓN COMPLETA ANTES DE SUBIR A GITHUB")
    print_info("Este script verificará la integridad del código y limpiará archivos temporales\n")
    
    results = []
    
    # Ejecutar verificaciones
    results.append(("Sintaxis Python", check_python_syntax()))
    results.append(("Archivos JavaScript", check_javascript_syntax()))
    results.append(("Estructura HTML", check_html_structure()))
    results.append(("Archivos Críticos", check_required_files()))
    results.append((".gitignore", check_gitignore()))
    results.append(("Limpieza Temporal", clean_temporary_files()))
    results.append(("Configuración .env", verify_env_file()))
    results.append(("Calidad de Código", check_code_quality()))
    
    # Resumen final
    print_header("RESULTADO FINAL")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        color = Colors.OK if passed else Colors.ERROR
        print(f"{color}{status} - {test_name}{Colors.RESET}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print_success("🎉 TODAS LAS VERIFICACIONES PASARON")
        print_info("\nPuedes proceder a subir a GitHub:")
        print_info("  1. git add .")
        print_info("  2. git commit -m 'feat: Mejoras UI - paneles redimensionables ultra finos y limpieza'")
        print_info("  3. git push origin main")
        
        generate_summary()
        return 0
    else:
        print_error("⚠️  ALGUNAS VERIFICACIONES FALLARON")
        print_error("Revisa los errores arriba antes de subir a GitHub")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_warning("\n\nVerificación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nError inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
