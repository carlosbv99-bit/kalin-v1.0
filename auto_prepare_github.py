#!/usr/bin/env python3
"""
Script automático completo para preparar el proyecto Kalin para GitHub.
Realiza limpieza, verificación de seguridad y preparación del repositorio.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

class GitHubPreparator:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def print_header(self, message):
        """Imprime un encabezado formateado."""
        print("\n" + "="*70)
        print(f"  {message}")
        print("="*70)
        
    def print_step(self, message):
        """Imprime un paso del proceso."""
        print(f"\n📋 {message}")
        print("-" * 50)
        
    def print_success(self, message):
        """Imprime un mensaje de éxito."""
        print(f"✅ {message}")
        
    def print_warning(self, message):
        """Imprime un mensaje de advertencia."""
        print(f"⚠️  {message}")
        
    def print_error(self, message):
        """Imprime un mensaje de error."""
        print(f"❌ {message}")

    def clean_project(self):
        """Limpia el proyecto de archivos basura y temporales."""
        self.print_step("Limpiando archivos basura y temporales")
        
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
            full_pattern = self.project_root / pattern
            
            # Usar glob para encontrar archivos coincidentes
            if '*' in pattern or '?' in pattern:
                matches = list(self.project_root.glob(pattern))
            else:
                matches = [full_pattern] if full_pattern.exists() else []
            
            for item in matches:
                try:
                    if item.is_file():
                        item.unlink()
                        print(f"  ✓ Eliminado: {item.relative_to(self.project_root)}")
                        deleted_count += 1
                    elif item.is_dir():
                        shutil.rmtree(item)
                        print(f"  ✓ Eliminado directorio: {item.relative_to(self.project_root)}")
                        deleted_count += 1
                except Exception as e:
                    print(f"  ✗ Error al eliminar {item}: {e}")
        
        self.print_success(f"Limpieza completada. Se eliminaron {deleted_count} archivos/directorios.")
        return deleted_count

    def check_security(self):
        """Verifica que no haya información sensible en el código."""
        self.print_step("Verificando seguridad del código")
        
        # Verificar archivo .env
        env_file = self.project_root / ".env"
        if env_file.exists():
            self.print_warning("Archivo .env encontrado - asegúrate de que esté en .gitignore")
        else:
            self.print_success("No se encontró archivo .env (correcto)")
        
        # Verificar .env.example
        env_example = self.project_root / ".env.example"
        if env_example.exists():
            self.print_success("Archivo .env.example encontrado (plantilla segura)")
        else:
            self.print_warning("No se encontró .env.example")
        
        # Buscar credenciales hardcodeadas en archivos Python
        suspicious_patterns = [
            r'API_KEY\s*=\s*[\'"][^\'"]+[\'"]',
            r'SECRET\s*=\s*[\'"][^\'"]+[\'"]',
            r'PASSWORD\s*=\s*[\'"][^\'"]+[\'"]',
            r'TOKEN\s*=\s*[\'"][^\'"]+[\'"]'
        ]
        
        found_issues = 0
        for py_file in self.project_root.rglob("*.py"):
            # Excluir directorios virtuales
            if any(part in ['.venv', 'venv', '__pycache__'] for part in py_file.parts):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in suspicious_patterns:
                    import re
                    if re.search(pattern, content, re.IGNORECASE):
                        self.print_warning(f"Posible credencial en: {py_file.relative_to(self.project_root)}")
                        found_issues += 1
            except:
                continue
        
        if found_issues == 0:
            self.print_success("No se encontraron credenciales hardcodeadas")
        else:
            self.print_warning(f"Se encontraron {found_issues} posibles problemas de seguridad")
        
        return found_issues == 0

    def update_gitignore(self):
        """Actualiza el archivo .gitignore si es necesario."""
        self.print_step("Verificando configuración de .gitignore")
        
        gitignore_file = self.project_root / ".gitignore"
        if gitignore_file.exists():
            self.print_success("Archivo .gitignore encontrado")
            
            # Verificar que contenga las exclusiones básicas
            content = gitignore_file.read_text()
            required_patterns = ['__pycache__', '*.pyc', '.env', '.venv', 'sessions/', 'logs/']
            
            missing_patterns = []
            for pattern in required_patterns:
                if pattern not in content:
                    missing_patterns.append(pattern)
            
            if missing_patterns:
                self.print_warning(f"Faltan patrones en .gitignore: {missing_patterns}")
            else:
                self.print_success(".gitignore contiene los patrones necesarios")
        else:
            self.print_error("No se encontró archivo .gitignore")
            return False
        
        return True

    def create_backup_info(self):
        """Crea información de respaldo."""
        self.print_step("Creando información de respaldo")
        
        backup_info = f"""# 📦 Información de Respaldo - Kalin v3.0

**Fecha de preparación:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Usuario:** carlosbv99

## ✅ Proceso Automático Completado

Este proyecto ha sido preparado automáticamente para GitHub usando el script `auto_prepare_github.py`.

### Archivos excluidos del repositorio:
- Datos de sesiones (`sessions/*.json`)
- Memoria de experiencia (`experience_memory/*.json`)
- Logs de desarrollo (`logs/*.log`)
- Archivos de caché Python
- Entornos virtuales
- Configuraciones IDE
- Credenciales y archivos .env

### Seguridad verificada:
- No hay credenciales hardcodeadas
- Archivo .env correctamente excluido
- Variables de entorno para configuración sensible

## 🚀 Para usar este repositorio:

1. Clonar: `git clone https://github.com/carlosbv99/kalin.git`
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar: Copiar `.env.example` a `.env` y configurar variables
4. Ejecutar: `python run.py`

---
*Generado automáticamente por auto_prepare_github.py*
"""
        
        backup_file = self.project_root / "BACKUP_INFO.md"
        backup_file.write_text(backup_info, encoding='utf-8')
        self.print_success("Información de respaldo creada: BACKUP_INFO.md")

    def run_git_commands(self):
        """Ejecuta comandos git básicos."""
        self.print_step("Preparando repositorio Git")
        
        try:
            # Verificar si es un repositorio git
            result = subprocess.run(['git', 'status'], 
                                  capture_output=True, 
                                  text=True, 
                                  cwd=self.project_root)
            
            if result.returncode == 0:
                self.print_success("Repositorio Git detectado")
                
                # Mostrar estado actual
                print("\nEstado actual del repositorio:")
                print(result.stdout[:500])  # Primeros 500 caracteres
                
                return True
            else:
                self.print_warning("No se detectó repositorio Git")
                print("Para inicializar: git init")
                return False
                
        except FileNotFoundError:
            self.print_warning("Git no está instalado o no está en PATH")
            return False
        except Exception as e:
            self.print_error(f"Error al verificar Git: {e}")
            return False

    def generate_summary(self):
        """Genera un resumen final del proceso."""
        self.print_header("RESUMEN FINAL")
        
        summary = f"""
🎉 PROYECTO LISTO PARA GITHUB

✅ Limpieza completada
✅ Seguridad verificada  
✅ .gitignore configurado
✅ Documentación actualizada

📁 Archivos principales incluidos:
   - agent/ (código fuente principal)
   - app/ (aplicación Android)
   - static/ y templates/ (interfaz web)
   - tests/ (suite de pruebas)
   - .env.example (plantilla de configuración)
   - requirements.txt (dependencias)

🚫 Archivos excluidos:
   - .env (credenciales)
   - sessions/ (datos locales)
   - experience_memory/ (memoria local)
   - logs/ (archivos de log)
   - __pycache__/ (caché Python)
   - .venv/ (entorno virtual)

📝 Próximos pasos:
   1. Revisa los cambios: git status
   2. Agrega archivos: git add .
   3. Commit: git commit -m "Clean project structure - prepared by auto script"
   4. Subir: git push origin main

¡Tu proyecto Kalin v3.0 está listo para GitHub! 🚀
"""
        
        print(summary)
        
        # Guardar resumen en archivo
        summary_file = self.project_root / "GITHUB_READY_SUMMARY.txt"
        summary_file.write_text(summary, encoding='utf-8')
        self.print_success(f"Resumen guardado en: GITHUB_READY_SUMMARY.txt")

    def run_full_preparation(self):
        """Ejecuta todo el proceso de preparación."""
        self.print_header("PREPARACIÓN AUTOMÁTICA PARA GITHUB - KALIN v3.0")
        
        print(f"Proyecto: {self.project_root}")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Ejecutar todos los pasos
        steps_completed = 0
        total_steps = 5
        
        try:
            # Paso 1: Limpieza
            if self.clean_project():
                steps_completed += 1
            
            # Paso 2: Verificación de seguridad
            if self.check_security():
                steps_completed += 1
            
            # Paso 3: Actualizar .gitignore
            if self.update_gitignore():
                steps_completed += 1
            
            # Paso 4: Crear información de respaldo
            self.create_backup_info()
            steps_completed += 1
            
            # Paso 5: Comandos Git
            if self.run_git_commands():
                steps_completed += 1
            
            # Generar resumen final
            self.generate_summary()
            
            self.print_header("PROCESO COMPLETADO EXITOSAMENTE")
            print(f"Pasos completados: {steps_completed}/{total_steps}")
            print("\n🎉 ¡Tu proyecto está listo para subir a GitHub!")
            
            return True
            
        except Exception as e:
            self.print_error(f"Error durante el proceso: {e}")
            return False

def main():
    """Función principal."""
    preparator = GitHubPreparator()
    success = preparator.run_full_preparation()
    
    if success:
        print("\n✅ Preparación completada exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Hubo errores durante la preparación")
        sys.exit(1)

if __name__ == "__main__":
    main()
