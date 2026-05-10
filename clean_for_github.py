#!/usr/bin/env python3
"""
Script de limpieza para preparar el proyecto Kalin para GitHub.
Elimina archivos temporales, cachés y archivos de desarrollo que no deben subirse al repositorio.
"""

import os
import shutil
import glob
from pathlib import Path

def clean_project():
    """Limpia el proyecto de archivos basura y temporales."""
    
    project_root = Path(__file__).parent
    
    print("🧹 Iniciando limpieza del proyecto Kalin...")
    print("=" * 60)
    
    # Archivos y patrones a eliminar
    patterns_to_delete = [
        # Cachés de Python
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        
        # Logs
        "**/*.log",
        
        # Archivos temporales
        "**/*.bak",
        "**/*.tmp",
        "**/*.temp",
        "**/*.cache",
        "**/*.pid",
        "**/*.seed",
        "**/*.lock",
        
        # Archivos del sistema
        "**/Thumbs.db",
        "**/desktop.ini",
        "**/.DS_Store",
        
        # Directorios de sesión y experiencia (datos locales)
        "sessions/*.json",
        "experience_memory/*.json",
        "logs/*.log",
        
        # Archivos de estado
        ".agent_state.json",
        "health_status.json",
        
        # Virtual environments
        ".venv",
        ".venv-1",
        "venv",
        "ENV",
        "env",
        
        # Gradle e IDE
        ".gradle",
        ".idea",
        ".kotlin",
        "*.iml",
        "local.properties",
        ".vscode",
        
        # Build directories
        "build",
        "*/build",
        "dist",
        
        # Cache directory
        "cache",
    ]
    
    deleted_count = 0
    
    for pattern in patterns_to_delete:
        full_pattern = project_root / pattern
        
        # Usar glob para encontrar archivos coincidentes
        if '*' in pattern or '?' in pattern:
            matches = list(project_root.glob(pattern))
        else:
            matches = [full_pattern] if full_pattern.exists() else []
        
        for item in matches:
            try:
                if item.is_file():
                    item.unlink()
                    print(f"✓ Eliminado archivo: {item.relative_to(project_root)}")
                    deleted_count += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    print(f"✓ Eliminado directorio: {item.relative_to(project_root)}")
                    deleted_count += 1
            except Exception as e:
                print(f"✗ Error al eliminar {item}: {e}")
    
    print("=" * 60)
    print(f"✅ Limpieza completada. Se eliminaron {deleted_count} archivos/directorios.")
    print("\n📝 Nota: Los archivos excluidos por .gitignore no se subirán a GitHub.")
    print("   Puedes verificar con: git status --ignored")

if __name__ == "__main__":
    clean_project()
