#!/usr/bin/env python3
"""
Kalin AI - Script de preparación y testing seguro
Este script reemplaza los archivos .bat y .ps1 eliminados por seguridad.

Uso:
    python run_tests.py
"""

import sys
import os
import subprocess


def limpiar_proyecto():
    """Limpia el proyecto antes de los tests."""
    print("[1/3] Limpiando proyecto...")
    
    try:
        result = subprocess.run([sys.executable, "prepare_for_testing.py"])
        if result.returncode != 0:
            print("ERROR en limpieza")
            return False
        print("✅ Limpieza completada")
        return True
    except Exception as e:
        print(f"Error en limpieza: {e}")
        return False


def ejecutar_tests():
    """Ejecuta la suite de tests completa."""
    print("\n[2/3] Ejecutando tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_suite_completa.py"])
        
        if result.returncode != 0:
            print()
            print("ADVERTENCIA: Algunos tests fallaron")
            print("Revisa los errores arriba antes de continuar")
            
            continuar = input("\n¿Deseas continuar de todas formas? (s/n): ")
            if continuar.lower() != "s":
                return False
        
        print("✅ Tests completados")
        return True
    
    except Exception as e:
        print(f"Error al ejecutar tests: {e}")
        return False


def iniciar_servidor():
    """Inicia el servidor de Kalin."""
    print("\n[3/3] Iniciando servidor...")
    print()
    print("=" * 40)
    print("Accede a http://localhost:5000")
    print("Presiona Ctrl+C para detener el servidor")
    print("=" * 40)
    print()
    
    try:
        subprocess.run([sys.executable, "run.py"])
    except KeyboardInterrupt:
        print("\n\nServidor detenido por el usuario.")
    except Exception as e:
        print(f"\nError al iniciar servidor: {e}")
        return False
    
    return True


def main():
    """Función principal."""
    print("=" * 80)
    print(" KALIN v3.0 - PREPARACION Y TESTING")
    print("=" * 80)
    print()
    
    # Paso 1: Limpiar
    if not limpiar_proyecto():
        input("\nPresiona Enter para salir...")
        sys.exit(1)
    
    # Paso 2: Tests
    if not ejecutar_tests():
        input("\nPresiona Enter para salir...")
        sys.exit(1)
    
    # Paso 3: Iniciar servidor
    iniciar_servidor()


if __name__ == "__main__":
    main()
