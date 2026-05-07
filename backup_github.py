#!/usr/bin/env python3
"""
Kalin AI - Script de backup seguro para GitHub
Este script reemplaza los archivos .bat y .ps1 eliminados por seguridad.

Uso:
    python backup_github.py [-m "Mensaje del commit"]
"""

import sys
import os
import subprocess
import argparse
from datetime import datetime


def verificar_git():
    """Verifica que Git esté instalado."""
    try:
        version = subprocess.check_output(
            ["git", "--version"], 
            stderr=subprocess.STDOUT
        ).decode().strip()
        print(f"✅ Git detectado: {version}")
        return True
    except Exception as e:
        print("❌ ERROR: Git no está instalado")
        print("Descarga Git desde: https://git-scm.com/downloads")
        return False


def inicializar_repo():
    """Inicializa el repositorio Git si no existe."""
    print("\n[1/7] Verificando repositorio Git...")
    
    if not os.path.exists(".git"):
        print("Inicializando repositorio Git...")
        subprocess.run(["git", "init"])
        print("✅ Repositorio inicializado")
    else:
        print("✅ Repositorio Git existente detectado")


def configurar_usuario():
    """Configura el usuario de Git."""
    print("[2/7] Configurando usuario Git...")
    subprocess.run(["git", "config", "user.name", "Kalin Backup"], 
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.email", "kalin@backup.local"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("✅ Usuario configurado")


def verificar_gitignore():
    """Crea o verifica el archivo .gitignore."""
    print("[3/7] Verificando archivo .gitignore...")
    
    if not os.path.exists(".gitignore"):
        print("Creando .gitignore...")
        
        gitignore_content = """# Python
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

# Virtual Environment
venv/
ENV/
env/
.venv/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Logs
logs/
*.log

# Cache
cache/

# Sessions
sessions/

# Environment variables
.env

# OS
.DS_Store
Thumbs.db

# Agent state
.agent_state.json

# Gradle (Android)
.gradle/
gradle-app.setting
!gradle-wrapper.jar

# Local properties
local.properties
"""
        
        with open(".gitignore", "w", encoding="utf-8") as f:
            f.write(gitignore_content)
        
        print("✅ .gitignore creado")
    else:
        print("✅ .gitignore existente")


def agregar_archivos():
    """Agrega archivos al staging."""
    print("[4/7] Agregando archivos al staging...")
    subprocess.run(["git", "add", "."])
    print("✅ Archivos agregados")


def crear_commit(mensaje=None):
    """Crea un commit con el mensaje especificado."""
    print("[5/7] Creando commit...")
    
    if not mensaje:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        mensaje = f"🔧 Backup automático - {timestamp}"
    
    result = subprocess.run(["git", "commit", "-m", mensaje])
    
    if result.returncode == 0:
        print("✅ Commit creado exitosamente")
        return True
    else:
        print("⚠️ No hay cambios para commitear o error en commit")
        return False


def crear_tag():
    """Crea un tag de versión."""
    print("[6/7] Creando tag de versión...")
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    version_tag = f"v1.0.0-backup-{timestamp}"
    
    subprocess.run(["git", "tag", "-a", version_tag, "-m", 
                   f"Backup automático - {datetime.now().strftime('%d/%m/%Y %H:%M')}"])
    
    print(f"✅ Tag creado: {version_tag}")


def verificar_remoto():
    """Verifica el remoto de GitHub."""
    print("[7/7] Verificando remoto GitHub...")
    
    try:
        remotes = subprocess.check_output(
            ["git", "remote", "-v"],
            stderr=subprocess.STDOUT
        ).decode()
        
        if "github.com" in remotes:
            print("✅ Remoto GitHub detectado")
            print()
            
            confirm = input("¿Deseas hacer push a GitHub? (S/N): ")
            if confirm.upper() == "S":
                print("Haciendo push a GitHub...")
                result = subprocess.run(["git", "push", "origin", "main", "--tags"])
                
                if result.returncode == 0:
                    print("✅ Push exitoso")
                else:
                    print("⚠️ Error en push. Intentando con master...")
                    subprocess.run(["git", "push", "origin", "master", "--tags"])
        else:
            print("⚠️ No se detectó remoto GitHub configurado")
            print()
            print("Para agregar un remoto GitHub:")
            print("  git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git")
            print("  git push -u origin main --tags")
    
    except Exception as e:
        print(f"⚠️ Error al verificar remoto: {e}")


def mostrar_resumen():
    """Muestra un resumen del backup."""
    print("\n" + "=" * 40)
    print("RESUMEN DEL BACKUP")
    print("=" * 40)
    print()
    
    print("📦 Últimos commits:")
    subprocess.run(["git", "log", "--oneline", "-5"])
    print()
    
    print("🏷️ Tags disponibles:")
    subprocess.run(["git", "tag", "-l"])
    print()
    
    print("📊 Estado actual:")
    subprocess.run(["git", "status", "--short"])
    print()
    
    print("=" * 40)
    print("✅ BACKUP COMPLETADO")
    print("=" * 40)


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Backup automático a GitHub")
    parser.add_argument("-m", "--message", help="Mensaje del commit", default=None)
    args = parser.parse_args()
    
    print("=" * 40)
    print("BACKUP VERSIONADO EN GITHUB - KALIN")
    print("=" * 40)
    print()
    
    # Verificar Git
    if not verificar_git():
        input("\nPresiona Enter para salir...")
        sys.exit(1)
    
    print()
    
    # Ejecutar pasos de backup
    inicializar_repo()
    print()
    
    configurar_usuario()
    print()
    
    verificar_gitignore()
    print()
    
    agregar_archivos()
    print()
    
    if crear_commit(args.message):
        print()
        crear_tag()
        print()
        verificar_remoto()
        print()
        mostrar_resumen()
    
    print()
    input("Presiona Enter para salir...")


if __name__ == "__main__":
    main()
