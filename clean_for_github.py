#!/usr/bin/env python3
"""
Kalin - Limpieza y Preparación para GitHub
===========================================
Este script limpia el proyecto de archivos innecesarios y lo prepara
para una copia de seguridad segura en GitHub.

Uso:
    python clean_for_github.py [--dry-run] [--verbose]

Opciones:
    --dry-run    Muestra qué se eliminaría sin borrar nada
    --verbose    Muestra información detallada
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# Configuración
PROJECT_ROOT = Path(__file__).parent
BACKUP_DIR = PROJECT_ROOT / "backups" / f"github_prep_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Archivos y directorios a EXCLUIR (no subir a GitHub)
EXCLUDE_PATTERNS = {
    # Directorios completos
    'directories': [
        '__pycache__',
        '.pytest_cache',
        '.gradle',
        '.idea',
        'node_modules',
        'venv',
        '.venv',
        'env',
        '.env',  # Directorio .env si existe
        'backups',  # Backups locales
        'logs',  # Logs de aplicación
        'sessions',  # Datos de sesión
        'experience_memory',  # Memoria local
        '.ollama',  # Modelos Ollama (muy grandes)
        'build',
        'dist',
        '*.egg-info',
    ],
    
    # Archivos específicos
    'files': [
        '.env',  # Variables de entorno con secrets
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.DS_Store',  # macOS
        'Thumbs.db',  # Windows
        '*.log',
        '*.pid',
        '*.sqlite',
        '*.db',
        'session_*.json',
        '.agent_state.json',
    ],
    
    # Archivos de desarrollo/temporales
    'temp_files': [
        'diagnose*.py',
        'test_*.py',  # Tests temporales (mantener tests/ oficial)
        'DEBUG*',
        'TODO*',
        'NOTES*',
        '*_backup*',
        '*_old*',
        '*_copy*',
    ],
    
    # Documentación redundante
    'redundant_docs': [
        'CAMBIOS_*.md',
        'CORRECCIONES_*.md',
        'DIAGNOSTICO_*.md',
        'CHECKLIST_*.txt',
        'INFORME_*.md',
        'RESUMEN_*.md',
        'CHANGELOG_*.md',
        'CHANGES_*.md',
        '*_SUMMARY.md',
        '*_UPDATE.md',
        'IMPLEMENTACION_*.md',
        'FIX_*.md',
        'SOLUCION_*.md',
        'AUDITORIA_*.md',
        'EVALUACION_*.md',
        'PREPARACION_*.md',
        'VERIFICATION_*.md',
        'REVIEW_*.md',
    ],
}

# Archivos que SÍ deben mantenerse
KEEP_FILES = [
    'README.md',
    'SECURITY.md',
    'requirements.txt',
    'main.py',
    'web.py',
    'run.py',
    'cli.py',
    'Dockerfile',
    'docker-compose.yml',
    '.gitignore',
    '.env.example',  # Template seguro
    'LICENSE',
]


def should_exclude(path: Path) -> tuple[bool, str]:
    """
    Determina si un archivo/directorio debe excluirse.
    
    Returns:
        (True, reason) si debe excluirse
        (False, "") si debe mantenerse
    """
    name = path.name
    
    # Verificar directorios
    if path.is_dir():
        for pattern in EXCLUDE_PATTERNS['directories']:
            if name == pattern or name.endswith(pattern):
                return True, f"Directorio excluido: {pattern}"
    
    # Verificar archivos específicos
    if path.is_file():
        # Archivos exactos
        for pattern in EXCLUDE_PATTERNS['files']:
            if name == pattern or name.endswith(pattern):
                return True, f"Archivo excluido: {pattern}"
        
        # Patrones glob
        import fnmatch
        for pattern in EXCLUDE_PATTERNS['temp_files'] + EXCLUDE_PATTERNS['redundant_docs']:
            if fnmatch.fnmatch(name, pattern):
                return True, f"Patrón excluido: {pattern}"
    
    return False, ""


def get_excluded_items(dry_run: bool = False) -> dict:
    """
    Obtiene lista de archivos y directorios a excluir.
    
    Returns:
        Diccionario con categorías de items excluidos
    """
    excluded = {
        'directories': [],
        'files': [],
        'total_size': 0
    }
    
    for item in PROJECT_ROOT.iterdir():
        # Ignorar directorios protegidos
        if item.name in ['.git', 'static', 'templates', 'agent', 'app']:
            continue
        
        should_excl, reason = should_exclude(item)
        if should_excl:
            try:
                size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file()) if item.is_dir() else item.stat().st_size
                excluded['total_size'] += size
                
                if item.is_dir():
                    excluded['directories'].append((item, reason, size))
                else:
                    excluded['files'].append((item, reason, size))
            except Exception as e:
                print(f"⚠️ Error calculando tamaño de {item}: {e}")
    
    return excluded


def format_size(size_bytes: int) -> str:
    """Formatea tamaño en bytes a formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def create_backup():
    """Crea backup de archivos importantes antes de limpiar"""
    print(f"\n📦 Creando backup en: {BACKUP_DIR}")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Backup de archivos críticos
    critical_files = ['.env', 'sessions', 'experience_memory']
    for item in critical_files:
        src = PROJECT_ROOT / item
        if src.exists():
            dst = BACKUP_DIR / item
            try:
                if src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
                print(f"  ✅ Backup: {item}")
            except Exception as e:
                print(f"  ⚠️ Error backup {item}: {e}")


def clean_project(dry_run: bool = False, verbose: bool = False):
    """
    Limpia el proyecto de archivos innecesarios.
    
    Args:
        dry_run: Si True, solo muestra qué se eliminaría
        verbose: Si True, muestra información detallada
    """
    print("=" * 70)
    print("  KALIN - LIMPIEZA PARA GITHUB")
    print("=" * 70)
    print()
    
    # Obtener items a excluir
    print("🔍 Analizando proyecto...")
    excluded = get_excluded_items(dry_run)
    
    print(f"\n📊 Resumen de limpieza:")
    print(f"   Directorios a eliminar: {len(excluded['directories'])}")
    print(f"   Archivos a eliminar: {len(excluded['files'])}")
    print(f"   Espacio a liberar: {format_size(excluded['total_size'])}")
    print()
    
    if not excluded['directories'] and not excluded['files']:
        print("✅ No hay archivos basura que eliminar")
        return
    
    # Mostrar detalles si verbose
    if verbose:
        print("📋 Detalles:")
        for item, reason, size in excluded['directories']:
            print(f"   📁 {item.name} ({format_size(size)}) - {reason}")
        for item, reason, size in excluded['files']:
            print(f"   📄 {item.name} ({format_size(size)}) - {reason}")
        print()
    
    # Confirmación
    if dry_run:
        print("ℹ️  DRY RUN - No se eliminó nada")
        print("   Usa sin --dry-run para ejecutar la limpieza real")
        return
    
    print("⚠️  ADVERTENCIA: Esta acción eliminará archivos permanentemente")
    response = input("   ¿Continuar? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("❌ Operación cancelada")
        return
    
    # Crear backup primero
    create_backup()
    
    # Eliminar directorios
    print("\n🗑️  Eliminando directorios...")
    for item, reason, size in sorted(excluded['directories'], key=lambda x: x[2], reverse=True):
        try:
            shutil.rmtree(item)
            print(f"   ✅ Eliminado: {item.name} ({format_size(size)})")
        except Exception as e:
            print(f"   ❌ Error eliminando {item.name}: {e}")
    
    # Eliminar archivos
    print("\n🗑️  Eliminando archivos...")
    for item, reason, size in sorted(excluded['files'], key=lambda x: x[2], reverse=True):
        try:
            item.unlink()
            print(f"   ✅ Eliminado: {item.name} ({format_size(size)})")
        except Exception as e:
            print(f"   ❌ Error eliminando {item.name}: {e}")
    
    print("\n" + "=" * 70)
    print("  ✅ LIMPIEZA COMPLETADA")
    print("=" * 70)
    print(f"\n📦 Backup creado en: {BACKUP_DIR}")
    print(f"💾 Espacio liberado: {format_size(excluded['total_size'])}")
    print("\n🚀 Proyecto listo para GitHub!")
    print("\nPróximos pasos:")
    print("   1. Revisa .gitignore para asegurar exclusiones correctas")
    print("   2. Ejecuta: git add .")
    print("   3. Ejecuta: git commit -m 'Limpieza para GitHub'")
    print("   4. Ejecuta: git push origin main")
    print()


def update_gitignore():
    """Actualiza .gitignore con reglas adicionales"""
    gitignore_path = PROJECT_ROOT / '.gitignore'
    
    additional_rules = """
# ===== KALIN - Reglas adicionales para GitHub =====

# Archivos de entorno y secrets
.env
*.secret
*.key
credentials.json

# Datos de sesión y estado
sessions/
.agent_state.json
*.session

# Logs y datos temporales
logs/
*.log
*.pid
tmp/
temp/

# Backups locales
backups/
*_backup_*
*_old_*

# Python cache
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE y editores
.idea/
.vscode/
*.swp
*.swo
*~
.DS_Store

# Gradle (Android)
.gradle/
build/
local.properties

# Node (si se usa frontend build)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Ollama models (muy grandes)
.ollama/
models/

# Experience memory (datos locales)
experience_memory/

# Test files temporales
test_*.py
diagnose*.py
debug*.py

# Documentation redundancy
CAMBIOS_*.md
CORRECCIONES_*.md
DIAGNOSTICO_*.md
CHECKLIST_*.txt
RESUMEN_*.md
CHANGELOG_*.md
IMPLEMENTACION_*.md
FIX_*.md
"""
    
    if gitignore_path.exists():
        current_content = gitignore_path.read_text()
        
        # Verificar si ya tiene las reglas
        if "# ===== KALIN - Reglas adicionales para GitHub =====" in current_content:
            print("✅ .gitignore ya está actualizado")
            return
        
        # Agregar reglas al final
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            f.write(additional_rules)
        
        print("✅ .gitignore actualizado con reglas adicionales")
    else:
        # Crear nuevo .gitignore
        gitignore_path.write_text(additional_rules, encoding='utf-8')
        print("✅ .gitignore creado")


def verify_clean_state():
    """Verifica que el proyecto esté limpio"""
    print("\n🔍 Verificando estado del proyecto...")
    
    excluded = get_excluded_items()
    
    if excluded['directories'] or excluded['files']:
        print(f"⚠️  Aún hay {len(excluded['directories'])} directorios y {len(excluded['files'])} archivos que deberían eliminarse")
        print("   Ejecuta el script nuevamente para completar la limpieza")
        return False
    else:
        print("✅ Proyecto limpio y listo para GitHub")
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Limpia el proyecto Kalin y lo prepara para GitHub',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python clean_for_github.py              # Limpieza normal
  python clean_for_github.py --dry-run    # Simular sin borrar
  python clean_for_github.py --verbose    # Mostrar detalles
        """
    )
    
    parser.add_argument('--dry-run', action='store_true',
                       help='Muestra qué se eliminaría sin borrar nada')
    parser.add_argument('--verbose', action='store_true',
                       help='Muestra información detallada')
    
    args = parser.parse_args()
    
    try:
        # Actualizar .gitignore primero
        update_gitignore()
        
        # Limpiar proyecto
        clean_project(dry_run=args.dry_run, verbose=args.verbose)
        
        # Verificar estado
        if not args.dry_run:
            verify_clean_state()
        
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
