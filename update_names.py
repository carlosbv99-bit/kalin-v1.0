"""Script para actualizar todas las referencias del proyecto Kalin"""
import os
import re
from pathlib import Path

def update_file_content(file_path):
    """Actualizar contenido de un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # Reemplazos de rutas
        content = re.sub(r'E:\\\\agente', r'E:\\kalin', content)
        content = re.sub(r'e:\\\\agente', r'e:\\kalin', content)
        content = re.sub(r'E:\kalin', r'E:\\kalin', content)
        content = re.sub(r'e:\kalin', r'e:\\kalin', content)
        
        # Reemplazos de nombres
        content = re.sub(r'Kalin', 'Kalin', content)
        content = re.sub(r'KALIN', 'KALIN', content)
        content = re.sub(r'Kalin', 'Kalin', content)
        content = re.sub(r'Kalin', 'Kalin', content)
        content = re.sub(r'tu Kalin', 'Kalin', content)
        content = re.sub(r'Soy tu Kalin', 'Soy Kalin', content)
        content = re.sub(r'KALIN_MODE', 'KALIN_MODE', content)
        
        # Solo escribir si hubo cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Actualizado: {file_path}")
            return True
        return False
        
    except Exception as e:
        print(f"✗ Error en {file_path}: {e}")
        return False

def main():
    """Actualizar todos los archivos del proyecto"""
    project_root = Path(r'E:\kalin')
    
    # Extensiones a procesar
    extensions = ['*.py', '*.html', '*.md', '*.txt', '*.json', '*.toml', '*.cfg']
    
    updated_count = 0
    
    for ext in extensions:
        for file_path in project_root.rglob(ext):
            # Ignorar directorios virtuales y de build
            if any(part in file_path.parts for part in ['.venv', '.venv-1', 'build', '__pycache__', '.git']):
                continue
            
            if update_file_content(file_path):
                updated_count += 1
    
    print(f"\n✅ Total de archivos actualizados: {updated_count}")

if __name__ == "__main__":
    main()
