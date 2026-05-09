#!/usr/bin/env python3
"""
Script de limpieza y backup automático para GitHub
Combina limpieza del proyecto + commit + push en un solo paso
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime


def limpiar_proyecto():
    """Limpia archivos temporales y caché"""
    print("="*80)
    print("🧹 PASO 1: LIMPIEZA DEL PROYECTO")
    print("="*80)
    print()
    
    # Limpiar __pycache__
    print("Eliminando __pycache__...")
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"  ✅ {pycache_path}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    # Limpiar archivos .pyc
    print("\nEliminando archivos .pyc...")
    count = 0
    for file in Path('.').rglob('*.pyc'):
        try:
            file.unlink()
            count += 1
        except:
            pass
    print(f"  ✅ {count} archivos eliminados")
    
    # Limpiar logs antiguos (más de 7 días)
    print("\nLimpiando logs antiguos...")
    log_dir = Path('logs')
    if log_dir.exists():
        for log_file in log_dir.glob('*.log'):
            if log_file.stat().st_size > 10 * 1024 * 1024:  # > 10MB
                try:
                    log_file.unlink()
                    print(f"  ✅ {log_file.name} (archivo grande)")
                except:
                    pass
    
    print("\n✅ Limpieza completada\n")


def verificar_git():
    """Verifica que Git esté disponible"""
    print("="*80)
    print("🔍 PASO 2: VERIFICANDO GIT")
    print("="*80)
    print()
    
    try:
        result = subprocess.run(['git', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Git disponible: {result.stdout.strip()}")
            return True
        else:
            print("❌ Git no encontrado")
            return False
    except Exception as e:
        print(f"❌ Error verificando Git: {e}")
        return False


def agregar_cambios():
    """Agrega todos los cambios al staging"""
    print("\n" + "="*80)
    print("📦 PASO 3: AGREGANDO CAMBIOS")
    print("="*80)
    print()
    
    print("Agregando archivos al staging...")
    result = subprocess.run(['git', 'add', '.'])
    
    if result.returncode == 0:
        print("✅ Archivos agregados")
        
        # Mostrar estado
        result = subprocess.run(['git', 'status', '--short'], 
                              capture_output=True, text=True)
        if result.stdout:
            cambios = len(result.stdout.strip().split('\n'))
            print(f"   📝 {cambios} archivos modificados")
        return True
    else:
        print("❌ Error al agregar archivos")
        return False


def crear_commit(mensaje=None):
    """Crea un commit con mensaje personalizado o automático"""
    print("\n" + "="*80)
    print("✏️  PASO 4: CREANDO COMMIT")
    print("="*80)
    print()
    
    if not mensaje:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        mensaje = f"🔧 Mejoras en generación HTML y soporte Linux - {timestamp}\n\n"
        mensaje += "- Aumentados tokens para HTML (800→1200)\n"
        mensaje += "- Timeout Ollama aumentado (30s→120s)\n"
        mensaje += "- Limpieza HTML más conservadora\n"
        mensaje += "- Scripts Linux/Mac creados (.sh)\n"
        mensaje += "- Validaciones relajadas para modelos locales\n"
        mensaje += "- Documentación actualizada"
    
    print(f"Mensaje del commit:\n{mensaje}\n")
    
    result = subprocess.run(['git', 'commit', '-m', mensaje])
    
    if result.returncode == 0:
        print("✅ Commit creado exitosamente")
        return True
    else:
        print("ℹ️  No hay cambios para commitear o error")
        return False


def crear_tag():
    """Crea un tag de versión"""
    print("\n" + "="*80)
    print("🏷️  PASO 5: CREANDO TAG")
    print("="*80)
    print()
    
    version = datetime.now().strftime("v1.0.%Y%m%d-%H%M")
    mensaje = f"Versión con mejoras HTML y soporte Linux - {datetime.now().strftime('%Y-%m-%d')}"
    
    result = subprocess.run(['git', 'tag', '-a', version, '-m', mensaje])
    
    if result.returncode == 0:
        print(f"✅ Tag creado: {version}")
        return version
    else:
        print("⚠️  No se pudo crear el tag")
        return None


def verificar_remoto():
    """Verifica si hay remoto configurado"""
    print("\n" + "="*80)
    print("🔗 PASO 6: VERIFICANDO REMOTO")
    print("="*80)
    print()
    
    try:
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True)
        if 'github.com' in result.stdout:
            print("✅ Remoto GitHub configurado:")
            print(result.stdout)
            return True
        else:
            print("⚠️  No hay remoto GitHub configurado")
            print("\nPara agregar un remoto:")
            print("  git remote add origin https://github.com/USUARIO/REPO.git")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def hacer_push():
    """Hace push a GitHub"""
    print("\n" + "="*80)
    print("🚀 PASO 7: HACIENDO PUSH A GITHUB")
    print("="*80)
    print()
    
    confirm = input("¿Deseas hacer push a GitHub? (s/n): ")
    if confirm.lower() != 's':
        print("Push omitido")
        return
    
    print("\nSubiendo cambios a GitHub...")
    
    # Intentar con main primero
    result = subprocess.run(['git', 'push', 'origin', 'main', '--tags'])
    
    if result.returncode != 0:
        print("⚠️  Falló con 'main', intentando con 'master'...")
        result = subprocess.run(['git', 'push', 'origin', 'master', '--tags'])
    
    if result.returncode == 0:
        print("\n✅ Push exitoso!")
        print("   Tu repositorio está actualizado en GitHub")
    else:
        print("\n❌ Error en el push")
        print("   Verifica tu conexión y credenciales")


def mostrar_resumen():
    """Muestra resumen final"""
    print("\n" + "="*80)
    print("📊 RESUMEN FINAL")
    print("="*80)
    print()
    
    # Últimos commits
    print("📦 Últimos 3 commits:")
    result = subprocess.run(['git', 'log', '--oneline', '-3'], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    # Tags
    print("\n🏷️  Últimos tags:")
    result = subprocess.run(['git', 'tag', '-l', '--sort=-version:refname'], 
                          capture_output=True, text=True)
    tags = result.stdout.strip().split('\n')[:3]
    for tag in tags:
        print(f"   {tag}")
    
    # Estado
    print("\n📝 Estado del repositorio:")
    result = subprocess.run(['git', 'status', '--short'], 
                          capture_output=True, text=True)
    if result.stdout:
        print(result.stdout[:500])  # Primeros 500 chars
    else:
        print("   Working tree clean ✅")
    
    print("\n" + "="*80)
    print("✅ BACKUP COMPLETADO EXITOSAMENTE")
    print("="*80)


def main():
    """Función principal"""
    print("\n" + "="*80)
    print("🔄 KALIN AI - LIMPIEZA Y BACKUP AUTOMÁTICO")
    print("="*80)
    print()
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('run.py'):
        print("❌ Error: Este script debe ejecutarse desde el directorio raíz de Kalin")
        sys.exit(1)
    
    # Paso 1: Limpiar
    limpiar_proyecto()
    
    # Paso 2: Verificar Git
    if not verificar_git():
        print("\n❌ Git es necesario para el backup")
        sys.exit(1)
    
    # Paso 3: Agregar cambios
    if not agregar_cambios():
        print("\n❌ No se pudieron agregar los cambios")
        sys.exit(1)
    
    # Paso 4: Crear commit
    if not crear_commit():
        print("\n⚠️  No se creó commit (posiblemente no hay cambios)")
    
    # Paso 5: Crear tag
    crear_tag()
    
    # Paso 6: Verificar remoto
    tiene_remoto = verificar_remoto()
    
    # Paso 7: Hacer push (si hay remoto)
    if tiene_remoto:
        hacer_push()
    
    # Mostrar resumen
    mostrar_resumen()
    
    print("\n✨ ¡Proceso completado!")
    print("\nPróximos pasos:")
    print("  1. Verifica tu repositorio en GitHub")
    print("  2. Revisa que todos los archivos estén subidos")
    print("  3. Si hay errores, ejecuta: git status")
    print()


if __name__ == "__main__":
    main()
