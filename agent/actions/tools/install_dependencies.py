"""
Herramienta para instalar dependencias Python automáticamente.
"""
import subprocess
import sys
import importlib


def verificar_dependencia(paquete: str) -> bool:
    """Verifica si un paquete está instalado"""
    try:
        importlib.import_module(paquete)
        return True
    except ImportError:
        return False


def instalar_dependencia(paquete: str) -> tuple[bool, str]:
    """
    Instala un paquete Python usando pip.
    
    Returns:
        (success: bool, message: str)
    """
    try:
        print(f"📦 Instalando {paquete}...")
        
        # Usar subprocess con seguridad (sin shell=True)
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", paquete],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minutos timeout
            check=False
        )
        
        if result.returncode == 0:
            print(f"✅ {paquete} instalado correctamente")
            return True, f"{paquete} instalado exitosamente"
        else:
            error_msg = result.stderr.strip()
            print(f"❌ Error instalando {paquete}: {error_msg}")
            return False, f"Error: {error_msg}"
            
    except subprocess.TimeoutExpired:
        msg = f"Timeout instalando {paquete} (>120s)"
        print(f"⏰ {msg}")
        return False, msg
    except Exception as e:
        msg = f"Excepción instalando {paquete}: {str(e)}"
        print(f"❌ {msg}")
        return False, msg


def instalar_multiples_dependencias(paquetes: list[str]) -> dict:
    """
    Instala múltiples paquetes y retorna resultados.
    
    Args:
        paquetes: Lista de nombres de paquetes
        
    Returns:
        Dict con resultados por paquete
    """
    resultados = {}
    
    for paquete in paquetes:
        # Verificar primero si ya está instalado
        if verificar_dependencia(paquete):
            print(f"✓ {paquete} ya está instalado")
            resultados[paquete] = {"installed": True, "message": "Ya instalado"}
        else:
            success, message = instalar_dependencia(paquete)
            resultados[paquete] = {"installed": success, "message": message}
    
    return resultados


def detectar_dependencias_desde_codigo(codigo: str) -> list[str]:
    """
    Detecta imports en código Python y extrae nombres de paquetes.
    
    Args:
        codigo: Código Python a analizar
        
    Returns:
        Lista de nombres de paquetes detectados
    """
    import re
    
    paquetes = set()
    
    # Detectar 'import X'
    imports = re.findall(r'^\s*import\s+(\w+)', codigo, re.MULTILINE)
    paquetes.update(imports)
    
    # Detectar 'from X import Y'
    from_imports = re.findall(r'^\s*from\s+(\w+)', codigo, re.MULTILINE)
    paquetes.update(from_imports)
    
    # Mapeo de módulos comunes a paquetes pip
    mapeo_modulo_paquete = {
        'PIL': 'pillow',
        'cv2': 'opencv-python',
        'sklearn': 'scikit-learn',
        'yaml': 'pyyaml',
        'bs4': 'beautifulsoup4',
        'dateutil': 'python-dateutil',
    }
    
    paquetes_mapeados = []
    for modulo in paquetes:
        paquete = mapeo_modulo_paquete.get(modulo, modulo)
        paquetes_mapeados.append(paquete)
    
    # Excluir paquetes estándar de Python
    paquetes_estandar = {
        'os', 'sys', 're', 'json', 'math', 'random', 'datetime',
        'collections', 'itertools', 'functools', 'pathlib', 'typing',
        'subprocess', 'importlib', 'unittest', 'logging', 'argparse',
        'io', 'string', 'time', 'copy', 'abc', 'enum', 'dataclasses'
    }
    
    paquetes_finales = [p for p in paquetes_mapeados if p not in paquetes_estandar]
    
    return paquetes_finales


if __name__ == '__main__':
    # Ejemplo de uso
    codigo_ejemplo = """
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import os
import json
"""
    
    print("Detectando dependencias...")
    dependencias = detectar_dependencias_desde_codigo(codigo_ejemplo)
    print(f"Dependencias detectadas: {dependencias}")
    
    print("\nInstalando dependencias faltantes...")
    resultados = instalar_multiples_dependencias(dependencias)
    
    print("\nResumen:")
    for paquete, resultado in resultados.items():
        status = "✅" if resultado["installed"] else "❌"
        print(f"  {status} {paquete}: {resultado['message']}")
