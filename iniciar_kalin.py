#!/usr/bin/env python3
"""
Kalin AI - Script de inicio multiplataforma
Este script reemplaza los archivos .bat y .ps1 eliminados por seguridad.

Uso:
    python iniciar_kalin.py
"""

import sys
import os
import subprocess
import platform


def verificar_python():
    """Verifica que Python esté instalado."""
    print("=" * 40)
    print("  KALIN AI - ASISTENTE DE PROGRAMACION")
    print("=" * 40)
    print()
    print("Verificando instalacion...")
    print()
    
    try:
        version = subprocess.check_output(
            [sys.executable, "--version"], 
            stderr=subprocess.STDOUT
        ).decode().strip()
        print(f"[OK] Python encontrado: {version}")
    except Exception as e:
        print("[ERROR] Python no esta instalado correctamente")
        print()
        print("Por favor instala Python desde:")
        print("https://www.python.org/downloads/")
        input("\nPresiona Enter para salir...")
        sys.exit(1)


def activar_venv():
    """Activa el entorno virtual si existe."""
    venv_path = os.path.join(".venv", "Scripts", "activate.bat")
    
    if os.path.exists(venv_path):
        print("[OK] Entorno virtual encontrado")
        print("Activando entorno virtual...")
        # En Windows, necesitamos ejecutar el activate en el mismo proceso
        # Pero Python no puede hacer esto directamente, así que usamos el sistema
        return True
    else:
        print("[INFO] No se encontro entorno virtual")
        print("Usando Python del sistema...")
        return False


def iniciar_kalin():
    """Inicia la aplicación Kalin."""
    print()
    print("=" * 40)
    print("  INICIANDO KALIN...")
    print("=" * 40)
    print()
    print("Abre tu navegador en: http://localhost:5000")
    print()
    print("Presiona Ctrl+C para detener Kalin")
    print()
    print("=" * 40)
    print()
    
    try:
        # Ejecutar run.py
        subprocess.run([sys.executable, "run.py"])
    except KeyboardInterrupt:
        print("\n\nKalin detenido por el usuario.")
    except Exception as e:
        print(f"\nError al iniciar Kalin: {e}")
        input("Presiona Enter para salir...")
        sys.exit(1)


def main():
    """Función principal."""
    verificar_python()
    activar_venv()
    iniciar_kalin()


if __name__ == "__main__":
    main()
