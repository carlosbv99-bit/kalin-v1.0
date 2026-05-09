#!/usr/bin/env python3
"""
Script de limpieza final antes de testing/producción
Elimina archivos temporales, caché y logs antiguos
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta


def clean_pycache():
    """Eliminar carpetas __pycache__"""
    print("🧹 Limpiando __pycache__...")
    count = 0
    
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                count += 1
                print(f"   ✅ Eliminado: {pycache_path}")
            except Exception as e:
                print(f"   ❌ Error eliminando {pycache_path}: {e}")
    
    print(f"   Total eliminados: {count}\n")


def clean_python_cache():
    """Eliminar archivos .pyc y .pyo"""
    print("🧹 Limpiando archivos .pyc y .pyo...")
    count = 0
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    count += 1
                except Exception as e:
                    print(f"   ❌ Error eliminando {file_path}: {e}")
    
    print(f"   Total eliminados: {count}\n")


def clean_old_logs(days=7):
    """Eliminar logs antiguos"""
    print(f"🧹 Limpiando logs antiguos (> {days} días)...")
    count = 0
    bytes_freed = 0
    
    log_dir = Path('logs')
    if not log_dir.exists():
        print("   No hay directorio de logs\n")
        return
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for log_file in log_dir.glob('*.log'):
        mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
        if mod_time < cutoff_date:
            size = log_file.stat().st_size
            try:
                log_file.unlink()
                count += 1
                bytes_freed += size
                print(f"   ✅ Eliminado: {log_file.name} ({size/1024:.1f} KB)")
            except Exception as e:
                print(f"   ❌ Error eliminando {log_file.name}: {e}")
    
    print(f"   Total eliminados: {count}")
    print(f"   Espacio liberado: {bytes_freed/1024/1024:.2f} MB\n")


def clean_session_files(days=30):
    """Eliminar sesiones antiguas"""
    print(f"🧹 Limpiando sesiones antiguas (> {days} días)...")
    count = 0
    bytes_freed = 0
    
    session_dir = Path('sessions')
    if not session_dir.exists():
        print("   No hay directorio de sessions\n")
        return
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for session_file in session_dir.glob('session_*.json'):
        mod_time = datetime.fromtimestamp(session_file.stat().st_mtime)
        if mod_time < cutoff_date:
            size = session_file.stat().st_size
            try:
                session_file.unlink()
                count += 1
                bytes_freed += size
                print(f"   ✅ Eliminado: {session_file.name}")
            except Exception as e:
                print(f"   ❌ Error eliminando {session_file.name}: {e}")
    
    print(f"   Total eliminados: {count}")
    print(f"   Espacio liberado: {bytes_freed/1024:.1f} KB\n")


def clean_backup_files():
    """Eliminar archivos de backup"""
    print("🧹 Limpiando archivos de backup (.bak, .backup, .old)...")
    count = 0
    bytes_freed = 0
    
    for root, dirs, files in os.walk('.'):
        # Saltar directorios ocultos y de sistema
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '.venv']]
        
        for file in files:
            if file.endswith(('.bak', '.backup', '.old', '~')):
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    os.remove(file_path)
                    count += 1
                    bytes_freed += size
                except Exception as e:
                    print(f"   ❌ Error eliminando {file_path}: {e}")
    
    print(f"   Total eliminados: {count}")
    print(f"   Espacio liberado: {bytes_freed/1024:.1f} KB\n")


def clean_temp_files():
    """Eliminar archivos temporales"""
    print("🧹 Limpiando archivos temporales...")
    count = 0
    bytes_freed = 0
    
    temp_patterns = ['*.tmp', '*.temp', '*.swp', '*.swo', '*~']
    
    for pattern in temp_patterns:
        for temp_file in Path('.').rglob(pattern):
            if temp_file.is_file():
                try:
                    size = temp_file.stat().st_size
                    temp_file.unlink()
                    count += 1
                    bytes_freed += size
                except Exception as e:
                    print(f"   ❌ Error eliminando {temp_file}: {e}")
    
    print(f"   Total eliminados: {count}")
    print(f"   Espacio liberado: {bytes_freed/1024:.1f} KB\n")


def get_directory_size(path='.'):
    """Calcular tamaño total del directorio"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        # Saltar directorios grandes que no queremos contar
        dirnames[:] = [d for d in dirnames if d not in ['.git', 'node_modules', 'venv', '.venv']]
        
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size


def main():
    print("="*80)
    print("🧹 LIMPIEZA FINAL KALIN v3.0")
    print("="*80)
    print()
    
    # Tamaño antes
    size_before = get_directory_size()
    print(f"📊 Tamaño actual del proyecto: {size_before/1024/1024:.2f} MB\n")
    
    # Ejecutar limpiezas
    clean_pycache()
    clean_python_cache()
    clean_old_logs(days=7)
    clean_session_files(days=30)
    clean_backup_files()
    clean_temp_files()
    
    # Tamaño después
    size_after = get_directory_size()
    freed = size_before - size_after
    
    print("="*80)
    print("✅ RESUMEN DE LIMPIEZA")
    print("="*80)
    print(f"Tamaño antes: {size_before/1024/1024:.2f} MB")
    print(f"Tamaño después: {size_after/1024/1024:.2f} MB")
    print(f"Espacio liberado: {freed/1024/1024:.2f} MB")
    print("="*80)
    print()
    print("✨ Proyecto limpio y listo para testing/producción")
    print()


if __name__ == "__main__":
    main()
