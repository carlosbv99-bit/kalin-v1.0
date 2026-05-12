"""
Script de Limpieza Exhaustiva - Preparación para Cambio Arquitectónico

Este script identifica y elimina:
1. Archivos de documentación redundantes/obsoletos
2. Scripts temporales de una sola vez
3. Backups innecesarios
4. Archivos de prueba obsoletos
5. Cachés y archivos temporales

IMPORTANTE: Revisa la lista antes de confirmar la eliminación
"""

import os
import shutil
from pathlib import Path

# Directorio raíz del proyecto
PROJECT_ROOT = Path(__file__).parent

# ===== CATEGORÍAS DE ARCHIVOS A ELIMINAR =====

# 1. DOCUMENTACIÓN REDUNDANTE (mantener solo README.md, CHANGELOG.md, CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md)
DOCS_TO_REMOVE = [
    # Documentos de implementación específicos (ya completados)
    "IMPLEMENTACION_*.md",
    "FIX_*.md",
    "CORRECCION_*.md",
    "CAMBIOS_*.md",
    
    # Resúmenes temporales
    "RESUMEN_*.md",
    "*_SUMMARY.md",
    "*_RESUMEN.md",
    
    # Guías específicas de tareas completadas
    "COMO_PROBAR_CAMBIOS.md",
    "COMO_USAR_SCRIPTS_GITHUB.md",
    "CONFIGURAR_BACKUP_RAPIDO.md",
    "COPIA_LIMPIA_INSTRUCCIONES.md",
    
    # Checklists temporales
    "CHECKLIST_*.txt",
    "CHECKLIST_*.md",
    
    # Diagnósticos ya resueltos
    "DIAGNOSTICO_*.md",
    "SOLUCION_*.md",
    
    # Preparaciones GitHub (ya completadas)
    "*GITHUB*.md",
    "*GITHUB*.txt",
    "PREPARACION_*.md",
    "LISTO_PARA_GITHUB.md",
    "INDICE_ARCHIVOS_GITHUB.md",
    
    # Evaluaciones (ya completadas)
    "EVALUACION_*.md",
    "AUDITORIA_*.md",
    
    # Arquitectura antigua
    "ARQUITECTURA_*.md",
    "DIAGRAMA_*.md",
    "MIGRACION_*.md",
    "FRONTEND_*.md",
    
    # Optimizaciones específicas
    "OPTIMIZACION_*.md",
    "TEMPERATURAS_*.md",
    
    # Features específicas ya documentadas en README
    "ANDROID_SUPPORT.md",
    "DOCKER_DEPLOYMENT.md",
    "MULTI_PROVIDER_SUMMARY.md",
    "ESCALABILIDAD_LLMS_RESUMEN.md",
    "NUEVOS_MODELOS_*.md",
    "PROVEEDORES_LLM_GUIA.md",
    "GUIA_MULTIPLES_LLMS.md",
    
    # Parches y diffs
    "PATCH_SYSTEM.md",
    "MENUS_HERRAMIENTAS_DIFFS.md",
    "IMPLEMENTACION_PATCHES_RESUMEN.md",
    
    # Memoria conversacional (ya integrada)
    "SISTEMA_MEMORIA_CONVERSACIONAL.md",
    "IMPLEMENTACION_MEMORIA_CONVERSACIONAL.md",
    "CORRECCIONES_MEMORIA_CONTEXTUAL.md",
    "EXPERIENCE_MEMORY_GUIDE.md",
    
    # Prompts dinámicos (ya integrado)
    "SISTEMA_PROMPTS_DINAMICOS.md",
    "NUEVA_ARQUITECTURA_PROMPTS.md",
    
    # Testing (ya documentado)
    "TESTING_GUIDE.md",
    "CI_CD_TESTING_GUIDE.md",
    "CODIGO_LIMPIO_TESTING.md",
    "REPARACIONES_TESTS.md",
    "GUIA_TESTS.md",
    "RUN_TEST.md",
    
    # Varios obsoletos
    "CHANGELOG_v1.1.md",
    "CHANGELOG_SIDEBAR_UPDATE.md",
    "CHANGES_TODAY.md",
    "REVIEW_SUMMARY.md",
    "EXECUTIVE_SUMMARY.md",
    "INFORME_ESTADO_PROYECTO.md",
    "INFORME_PROYECTO.pdf",
    "README.pdf",
    "README_KALIN_V3.md",
    "README_PROFESSIONAL.md",
    "README_LINUX.md",
    "README_GITHUB.md",
    "QUICK_START_SPECIALISTS.md",
    "DEPLOYMENTS.md",
    "ROADMAP_IDE_AUTONOMO.md",
    "BRANCH_PROTECTION_SETUP.md",
    
    # Scripts de preparación GitHub
    "AUTO_GITHUB_INSTRUCTIONS.txt",
    "BACKUP_GITHUB_GUIA.md",
    "BACKUP_RAPIDO.md",
    "GITHUB_PREP_REPORT.txt",
    "INICIO_RAPIDO_GITHUB.txt",
    "INSTRUCCIONES_SIMPLES_GITHUB.txt",
    "INSTRUCCIONES_SUBIR_GITHUB.md",
    "SCRIPTS_AUTOMATICOS.md",
]

# 2. SCRIPTS TEMPORALES/OBSOLETOS
SCRIPTS_TO_REMOVE = [
    # Scripts de backup (redundantes)
    "backup_*.py",
    "clean_github_trash.ps1",
    "prepare_for_github.ps1",
    "prepare_github.bat",
    "commit_and_push.ps1",
    "commit_v1.1.ps1",
    
    # Scripts de preparación one-time
    "auto_github_prep.py",
    "auto_github_prep.ps1",
    "auto_prepare_github.py",
    "prepare_for_review.py",
    "prepare_for_testing.py",
    "verify_before_github.py",
    "verify_github_ready.py",
    "setup_auto_backup.py",
    
    # Scripts de limpieza específicos
    "clean_copy_project.bat",
    "clean_copy_project.py",
    "clean_disk_space.py",
    "limpieza_backup_avanzado.py",
    "delete_backups.bat",
    
    # Scripts de diagnóstico temporal
    "diagnose.py",
    "diagnose_imports.py",
    "check_provider.py",
    "check_mimo_config.py",
    "verify_repairs.py",
    "fix_index.py",
    "update_names.py",
    "git_fix.py",
    "auto_fix.py",
    
    # Scripts de testing antiguos
    "test_flow_and_functionality.py",
    "test_general.py",
    "test_general_workflow.py",
    "test_quick.py",
    "run_all_tests.py",
    
    # Otros scripts no esenciales
    "crear_readme.py",
    "generar_pdf.py",
    "security_audit.py",
    "check_code_quality.py",
    "maintenance.py",
    "ejemplo_patch_system.py",
    "EJEMPLOS_PRACTICOS.py",
]

# 3. ARCHIVOS DE CONFIGURACIÓN ANDROID/GRADLE (si no se usa Android)
ANDROID_FILES = [
    "app/",
    "gradle/",
    "build.gradle.kts",
    "settings.gradle.kts",
    "gradle.properties",
    "gradlew",
    "gradlew.bat",
    "local.properties",
    "main.dart",
]

# 4. DIRECTORIOS A ELIMINAR
DIRS_TO_REMOVE = [
    "backups/",  # Backups locales (deberían estar en Git)
    "__pycache__/",
    ".gradle/",
]

# 5. ARCHIVOS EN RAÍZ QUE SE PUEDEN MOVER
FILES_TO_REVIEW = [
    "reiniciar_servidor.bat",
    "iniciar_kalin.sh",
    "instalar_linux.sh",
]


def collect_files_to_remove(patterns, directory=PROJECT_ROOT):
    """Recopila archivos que coinciden con los patrones"""
    import fnmatch
    
    files = []
    for pattern in patterns:
        if '*' in pattern:
            # Patrón con wildcard
            for file in directory.glob(pattern):
                if file.is_file():
                    files.append(file)
        else:
            # Archivo específico
            file_path = directory / pattern
            if file_path.exists():
                if file_path.is_file():
                    files.append(file_path)
                elif file_path.is_dir():
                    files.append(file_path)
    
    return list(set(files))  # Eliminar duplicados


def calculate_size(path):
    """Calcula el tamaño total de un archivo o directorio"""
    if path.is_file():
        return path.stat().st_size
    elif path.is_dir():
        total = 0
        for item in path.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
        return total
    return 0


def format_size(size_bytes):
    """Formatea tamaño en bytes a formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def main():
    print("=" * 80)
    print("🧹 LIMPIEZA EXHAUSTIVA DEL PROYECTO KALIN")
    print("=" * 80)
    print()
    print("⚠️  ADVERTENCIA: Esta operación eliminará archivos permanentemente")
    print("   Revisa cuidadosamente la lista antes de confirmar\n")
    
    # Recopilar todos los archivos a eliminar
    all_files = []
    
    print("📋 Analizando archivos...")
    
    # Documentación
    docs = collect_files_to_remove(DOCS_TO_REMOVE)
    all_files.extend(docs)
    print(f"   📄 Documentación redundante: {len(docs)} archivos")
    
    # Scripts
    scripts = collect_files_to_remove(SCRIPTS_TO_REMOVE)
    all_files.extend(scripts)
    print(f"   🔧 Scripts temporales: {len(scripts)} archivos")
    
    # Android
    android = collect_files_to_remove(ANDROID_FILES)
    all_files.extend(android)
    print(f"   📱 Archivos Android/Gradle: {len(android)} archivos/dirs")
    
    # Directorios
    dirs = collect_files_to_remove(DIRS_TO_REMOVE)
    all_files.extend(dirs)
    print(f"   📁 Directorios: {len(dirs)} directorios")
    
    # Calcular espacio a liberar
    total_size = sum(calculate_size(f) for f in all_files)
    
    print("\n" + "=" * 80)
    print(f"📊 RESUMEN DE LIMPIEZA")
    print("=" * 80)
    print(f"   Total archivos/directorios: {len(all_files)}")
    print(f"   Espacio a liberar: {format_size(total_size)}")
    print()
    
    # Mostrar lista detallada
    print("📝 ARCHIVOS/DIRECTORIOS A ELIMINAR:")
    print("-" * 80)
    
    for i, file in enumerate(sorted(all_files), 1):
        size = format_size(calculate_size(file))
        rel_path = file.relative_to(PROJECT_ROOT)
        type_icon = "📁" if file.is_dir() else "📄"
        print(f"   {i:3d}. {type_icon} {rel_path} ({size})")
    
    print("-" * 80)
    print()
    
    # Confirmación
    response = input("❓ ¿Confirmar eliminación? (escribe 'ELIMINAR' para confirmar): ")
    
    if response.strip() != 'ELIMINAR':
        print("\n❌ Operación cancelada")
        return
    
    # Ejecutar eliminación
    print("\n🗑️  Eliminando archivos...")
    deleted_count = 0
    failed_count = 0
    
    for file in all_files:
        try:
            if file.is_dir():
                shutil.rmtree(file)
            else:
                file.unlink()
            deleted_count += 1
            print(f"   ✅ {file.relative_to(PROJECT_ROOT)}")
        except Exception as e:
            failed_count += 1
            print(f"   ❌ Error eliminando {file.relative_to(PROJECT_ROOT)}: {e}")
    
    print("\n" + "=" * 80)
    print("✅ LIMPIEZA COMPLETADA")
    print("=" * 80)
    print(f"   Eliminados: {deleted_count} archivos/directorios")
    print(f"   Fallidos: {failed_count}")
    print(f"   Espacio liberado: ~{format_size(total_size)}")
    print()
    print("💡 Sugerencia: Ejecuta 'git status' para ver los cambios")


if __name__ == "__main__":
    main()
