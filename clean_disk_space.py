"""
Script para limpiar espacio en disco del proyecto Kalin.
Elimina archivos temporales, logs antiguos, caché y backups.
"""

import os
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta

def get_folder_size(path):
    """Calcula el tamaño de una carpeta en MB"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
    except Exception as e:
        print(f"Error al calcular tamaño de {path}: {e}")
    return total_size / (1024 * 1024)  # Convertir a MB

def format_size(size_mb):
    """Formatea el tamaño en MB o GB"""
    if size_mb >= 1024:
        return f"{size_mb / 1024:.2f} GB"
    return f"{size_mb:.2f} MB"

def analyze_disk_usage():
    """Analiza el uso de disco del proyecto"""
    print("="*80)
    print("📊 ANÁLISIS DE USO DE DISCO - KALIN")
    print("="*80)
    
    base_path = Path(__file__).parent
    
    # Carpetas principales a analizar
    folders_to_check = [
        'logs',
        'sessions',
        'experience_memory',
        'cache',
        '__pycache__',
        '.gradle',
        'app/build',
        '.venv',
        '.venv-1',
    ]
    
    total_project_size = get_folder_size(str(base_path))
    print(f"\n📁 Tamaño total del proyecto: {format_size(total_project_size)}\n")
    
    print("Desglose por carpetas:")
    print("-" * 80)
    
    folder_sizes = []
    for folder in folders_to_check:
        folder_path = base_path / folder
        if folder_path.exists():
            size = get_folder_size(str(folder_path))
            folder_sizes.append((folder, size))
            print(f"  {folder:30} {format_size(size):>15}")
    
    print("-" * 80)
    
    # Archivos .bak en el directorio raíz
    bak_files = list(base_path.glob("*.bak"))
    if bak_files:
        bak_size = sum(f.stat().st_size for f in bak_files) / (1024 * 1024)
        folder_sizes.append(('archivos .bak', bak_size))
        print(f"  {'archivos .bak':30} {format_size(bak_size):>15} ({len(bak_files)} archivos)")
    
    print()
    return folder_sizes, base_path

def clean_logs(older_than_days=7):
    """Limpia logs antiguos"""
    print("\n" + "="*80)
    print("🧹 LIMPIANDO LOGS ANTIGUOS")
    print("="*80)
    
    logs_path = Path(__file__).parent / 'logs'
    if not logs_path.exists():
        print("✅ No hay carpeta de logs")
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=older_than_days)
    cleaned_size = 0
    cleaned_count = 0
    
    for log_file in logs_path.glob("*.log"):
        file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        if file_mtime < cutoff_date:
            file_size = log_file.stat().st_size
            cleaned_size += file_size
            log_file.unlink()
            cleaned_count += 1
            print(f"  🗑️  Eliminado: {log_file.name} ({file_size / 1024:.2f} KB)")
    
    # También limpiar logs vacíos o muy pequeños (< 1KB)
    for log_file in logs_path.glob("*.log"):
        if log_file.stat().st_size < 1024:
            cleaned_size += log_file.stat().st_size
            log_file.unlink()
            cleaned_count += 1
            print(f"  🗑️  Eliminado (vacío): {log_file.name}")
    
    print(f"\n✅ Logs eliminados: {cleaned_count} archivos")
    print(f"💾 Espacio liberado: {cleaned_size / (1024 * 1024):.2f} MB")
    
    return cleaned_size

def clean_sessions(older_than_days=30):
    """Limpia sesiones antiguas"""
    print("\n" + "="*80)
    print("🧹 LIMPIANDO SESIONES ANTIGUAS")
    print("="*80)
    
    sessions_path = Path(__file__).parent / 'sessions'
    if not sessions_path.exists():
        print("✅ No hay carpeta de sesiones")
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=older_than_days)
    cleaned_size = 0
    cleaned_count = 0
    
    for session_file in sessions_path.glob("session_*.json"):
        file_mtime = datetime.fromtimestamp(session_file.stat().st_mtime)
        if file_mtime < cutoff_date:
            file_size = session_file.stat().st_size
            cleaned_size += file_size
            session_file.unlink()
            cleaned_count += 1
            print(f"  🗑️  Eliminado: {session_file.name}")
    
    print(f"\n✅ Sesiones eliminadas: {cleaned_count} archivos")
    print(f"💾 Espacio liberado: {cleaned_size / (1024 * 1024):.2f} MB")
    
    return cleaned_size

def clean_pycache():
    """Limpia carpetas __pycache__"""
    print("\n" + "="*80)
    print("🧹 LIMPIANDO CACHE DE PYTHON")
    print("="*80)
    
    base_path = Path(__file__).parent
    cleaned_size = 0
    cleaned_count = 0
    
    for pycache_dir in base_path.rglob("__pycache__"):
        if pycache_dir.is_dir():
            dir_size = get_folder_size(str(pycache_dir))
            cleaned_size += dir_size * 1024 * 1024  # Convertir MB a bytes
            try:
                shutil.rmtree(pycache_dir)
                cleaned_count += 1
                print(f"  🗑️  Eliminado: {pycache_dir.relative_to(base_path)}")
            except Exception as e:
                print(f"  ❌ Error al eliminar {pycache_dir}: {e}")
    
    print(f"\n✅ Carpetas __pycache__ eliminadas: {cleaned_count}")
    print(f"💾 Espacio liberado: {cleaned_size / (1024 * 1024):.2f} MB")
    
    return cleaned_size

def clean_backup_files():
    """Limpia archivos .bak"""
    print("\n" + "="*80)
    print("🧹 LIMPIANDO ARCHIVOS DE BACKUP")
    print("="*80)
    
    base_path = Path(__file__).parent
    cleaned_size = 0
    cleaned_count = 0
    
    for bak_file in base_path.rglob("*.bak"):
        file_size = bak_file.stat().st_size
        cleaned_size += file_size
        try:
            bak_file.unlink()
            cleaned_count += 1
            print(f"  🗑️  Eliminado: {bak_file.relative_to(base_path)} ({file_size / 1024:.2f} KB)")
        except Exception as e:
            print(f"  ❌ Error al eliminar {bak_file}: {e}")
    
    print(f"\n✅ Archivos .bak eliminados: {cleaned_count}")
    print(f"💾 Espacio liberado: {cleaned_size / (1024 * 1024):.2f} MB")
    
    return cleaned_size

def clean_gradle_cache():
    """Limpia caché de Gradle"""
    print("\n" + "="*80)
    print("🧹 LIMPIANDO CACHE DE GRADLE")
    print("="*80)
    
    gradle_path = Path(__file__).parent / '.gradle'
    if not gradle_path.exists():
        print("✅ No hay caché de Gradle")
        return 0
    
    cleaned_size = get_folder_size(str(gradle_path)) * 1024 * 1024
    
    try:
        shutil.rmtree(gradle_path)
        print(f"  🗑️  Carpeta .gradle eliminada completamente")
        print(f"💾 Espacio liberado: {cleaned_size / (1024 * 1024):.2f} MB")
    except Exception as e:
        print(f"  ❌ Error al eliminar .gradle: {e}")
        return 0
    
    return cleaned_size

def suggest_ollama_cleanup():
    """Sugiere limpieza de modelos Ollama"""
    print("\n" + "="*80)
    print("🦙 LIMPIEZA DE MODELOS OLLAMA")
    print("="*80)
    
    print("\n⚠️  Los modelos de Ollama pueden ocupar mucho espacio.")
    print("   Ubicación típica: C:\\Users\\TU_USUARIO\\.ollama\\models")
    print()
    print("Para ver modelos instalados:")
    print("  ollama list")
    print()
    print("Para eliminar modelos no utilizados:")
    print("  ollama rm qwen2.5:7b      # Si no lo usas")
    print("  ollama rm llama3.2        # Ya no lo necesitas")
    print("  ollama rm codellama:7b    # Si no lo usas")
    print()
    print("💡 RECOMENDACIÓN: Mantén solo deepseek-coder:latest")
    print("   Esto puede liberar 5-15 GB dependiendo de los modelos instalados")
    print()

def main():
    print("\n" + "="*80)
    print("🧹 SCRIPT DE LIMPIEZA - KALIN")
    print("="*80)
    print()
    print("Este script te ayudará a liberar espacio en disco eliminando:")
    print("  • Logs antiguos (>7 días)")
    print("  • Sesiones antiguas (>30 días)")
    print("  • Cache de Python (__pycache__)")
    print("  • Archivos de backup (.bak)")
    print("  • Caché de Gradle (se regenera automáticamente)")
    print()
    
    confirm = input("¿Deseas continuar? (s/n): ").strip().lower()
    if confirm != 's':
        print("❌ Limpieza cancelada")
        return
    
    # Analizar uso actual
    folder_sizes, base_path = analyze_disk_usage()
    
    # Ejecutar limpiezas
    total_cleaned = 0
    
    total_cleaned += clean_logs(older_than_days=7)
    total_cleaned += clean_sessions(older_than_days=30)
    total_cleaned += clean_pycache()
    total_cleaned += clean_backup_files()
    
    # Preguntar sobre Gradle
    gradle_path = base_path / '.gradle'
    if gradle_path.exists():
        gradle_size = get_folder_size(str(gradle_path))
        print(f"\n📁 Caché de Gradle detectado: {format_size(gradle_size)}")
        clean_gradle_confirm = input("¿Eliminar caché de Gradle? (s/n): ").strip().lower()
        if clean_gradle_confirm == 's':
            total_cleaned += clean_gradle_cache()
    
    # Sugerencias de Ollama
    suggest_ollama_cleanup()
    
    # Resumen final
    print("\n" + "="*80)
    print("📊 RESUMEN DE LIMPIEZA")
    print("="*80)
    print(f"💾 Espacio total liberado: {total_cleaned / (1024 * 1024):.2f} MB")
    print()
    print("✅ ¡Limpieza completada!")
    print()
    
    # Verificar tamaño final
    final_size = get_folder_size(str(base_path))
    print(f"📁 Tamaño final del proyecto: {format_size(final_size)}")
    print()

if __name__ == "__main__":
    main()
