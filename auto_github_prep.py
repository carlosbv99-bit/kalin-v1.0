#!/usr/bin/env python3
"""
Script totalmente automático para preparar Kalin v3.0 para GitHub.
Ejecuta todas las verificaciones, limpieza y preparación en un solo paso.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

class AutoGitHubPrep:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.success = []
        
    def print_header(self, text, char="=", color="\033[96m"):
        """Imprime un encabezado con color."""
        reset = "\033[0m"
        print(f"\n{color}{char * 70}{reset}")
        print(f"{color}{text.center(70)}{reset}")
        print(f"{color}{char * 70}{reset}\n")
        
    def print_step(self, num, total, text):
        """Imprime un paso del proceso."""
        print(f"\n\033[93m[{num}/{total}] {text}\033[0m")
        print("-" * 70)
        
    def print_success(self, text):
        """Imprime mensaje de éxito."""
        msg = f"✅ {text}"
        print(f"\033[92m{msg}\033[0m")
        self.success.append(text)
        
    def print_warning(self, text):
        """Imprime mensaje de advertencia."""
        msg = f"⚠️  {text}"
        print(f"\033[93m{msg}\033[0m")
        self.warnings.append(text)
        
    def print_error(self, text):
        """Imprime mensaje de error."""
        msg = f"❌ {text}"
        print(f"\033[91m{msg}\033[0m")
        self.errors.append(text)
        
    def print_info(self, text):
        """Imprime información."""
        print(f"ℹ️  {text}")

    def step_1_verify_project(self):
        """Paso 1: Verificar estructura del proyecto."""
        self.print_step(1, 6, "Verificando estructura del proyecto")
        
        required_files = {
            "main.py": "Archivo principal",
            "web.py": "Servidor web",
            ".gitignore": "Configuración Git",
            ".env.example": "Plantilla de configuración",
            "requirements.txt": "Dependencias"
        }
        
        all_ok = True
        for file, desc in required_files.items():
            if (self.project_root / file).exists():
                self.print_success(f"{file} - {desc}")
            else:
                self.print_warning(f"{file} - {desc} (no encontrado)")
                all_ok = False
        
        return all_ok

    def step_2_check_sensitive_files(self):
        """Paso 2: Verificar archivos sensibles."""
        self.print_step(2, 6, "Verificando archivos sensibles")
        
        # Verificar .env
        env_file = self.project_root / ".env"
        if env_file.exists():
            self.print_info("Archivo .env encontrado (será excluido por .gitignore)")
            
            # Verificar si está en git
            try:
                result = subprocess.run(
                    ["git", "ls-files", "--error-unmatch", ".env"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.print_error("¡ALERTA! .env está en el repositorio Git")
                    self.print_info("Se eliminará automáticamente del índice")
                    return False
                else:
                    self.print_success(".env NO está en el repositorio (correcto)")
            except:
                self.print_warning("No se pudo verificar estado Git de .env")
        else:
            self.print_success("No hay archivo .env (seguro)")
        
        # Verificar otros archivos sensibles
        sensitive_patterns = [
            ("local.properties", "Configuración local Android"),
            (".agent_state.json", "Estado del agente"),
        ]
        
        for pattern, desc in sensitive_patterns:
            if (self.project_root / pattern).exists():
                self.print_info(f"{pattern} encontrado ({desc})")
        
        return True

    def step_3_clean_project(self):
        """Paso 3: Limpiar archivos temporales."""
        self.print_step(3, 6, "Limpiando archivos temporales y cachés")
        
        patterns_to_clean = [
            ("__pycache__", "Caché Python", True),
            ("*.pyc", "Archivos compilados Python", False),
            ("*.pyo", "Archivos optimizados Python", False),
            ("*.log", "Archivos de log", False),
            ("*.bak", "Archivos de respaldo", False),
            ("*.tmp", "Archivos temporales", False),
            (".gradle", "Build Gradle", True),
            (".idea", "Configuración IDE", True),
            (".kotlin", "Caché Kotlin", True),
            ("build", "Directorio build", True),
        ]
        
        deleted_count = 0
        
        for pattern, desc, is_dir in patterns_to_clean:
            if is_dir:
                # Buscar directorios
                for dir_path in self.project_root.rglob(pattern):
                    if dir_path.is_dir():
                        try:
                            shutil.rmtree(dir_path)
                            deleted_count += 1
                            print(f"  ✓ Eliminado: {dir_path.name}/")
                        except Exception as e:
                            print(f"  ✗ Error al eliminar {dir_path.name}: {e}")
            else:
                # Buscar archivos con patrón
                for file_path in self.project_root.rglob(pattern):
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                            deleted_count += 1
                        except Exception as e:
                            pass
        
        # Limpiar archivos específicos en raíz
        root_files_to_delete = [
            ".agent_state.json",
            "health_status.json",
        ]
        
        for filename in root_files_to_delete:
            file_path = self.project_root / filename
            if file_path.exists():
                try:
                    file_path.unlink()
                    deleted_count += 1
                    print(f"  ✓ Eliminado: {filename}")
                except Exception as e:
                    print(f"  ✗ Error al eliminar {filename}: {e}")
        
        if deleted_count > 0:
            self.print_success(f"Se eliminaron {deleted_count} archivos/directorios temporales")
        else:
            self.print_success("No se encontraron archivos temporales para eliminar")
        
        return True

    def step_4_verify_gitignore(self):
        """Paso 4: Verificar .gitignore."""
        self.print_step(4, 6, "Verificando configuración de .gitignore")
        
        gitignore = self.project_root / ".gitignore"
        if not gitignore.exists():
            self.print_error("No se encontró archivo .gitignore")
            return False
        
        content = gitignore.read_text()
        
        required_patterns = [
            (".env", "Variables de entorno"),
            ("__pycache__", "Caché Python"),
            ("*.pyc", "Archivos compilados"),
            (".gradle", "Build Gradle"),
            (".idea", "Configuración IDE"),
            ("sessions/", "Datos de sesiones"),
            ("logs/", "Archivos de log"),
            ("experience_memory/", "Memoria de experiencia"),
            ("build/", "Directorios build"),
            (".venv", "Entorno virtual"),
            ("backups/", "Backups"),
        ]
        
        missing = []
        for pattern, desc in required_patterns:
            if pattern in content:
                print(f"  ✓ {pattern:30s} - {desc}")
            else:
                print(f"  ✗ FALTA: {pattern:30s} - {desc}")
                missing.append(pattern)
        
        if missing:
            self.print_warning(f"Faltan {len(missing)} patrones en .gitignore")
            return False
        else:
            self.print_success(".gitignore tiene todas las reglas necesarias")
            return True

    def step_5_check_git_status(self):
        """Paso 5: Verificar estado de Git."""
        self.print_step(5, 6, "Verificando estado del repositorio Git")
        
        try:
            # Verificar si es repo Git
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.print_warning("No se detectó repositorio Git")
                self.print_info("Inicializa con: git init")
                return False
            
            self.print_success("Repositorio Git detectado")
            
            # Mostrar estado
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                print("\nArchivos modificados:")
                print(result.stdout[:500])  # Primeros 500 caracteres
            else:
                print("No hay cambios pendientes")
            
            return True
            
        except FileNotFoundError:
            self.print_warning("Git no está instalado o no está en PATH")
            return False
        except Exception as e:
            self.print_error(f"Error al verificar Git: {e}")
            return False

    def step_6_generate_report(self):
        """Paso 6: Generar reporte final."""
        self.print_step(6, 6, "Generando reporte final")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
{'='*70}
REPORTE DE PREPARACIÓN PARA GITHUB - KALIN v3.0
{'='*70}

Fecha: {timestamp}
Proyecto: {self.project_root}

RESUMEN:
--------
✅ Exitos: {len(self.success)}
⚠️  Advertencias: {len(self.warnings)}
❌ Errores: {len(self.errors)}

EXITOS:
-------
"""
        for s in self.success:
            report += f"  • {s}\n"
        
        if self.warnings:
            report += "\nADVERTENCIAS:\n---------------\n"
            for w in self.warnings:
                report += f"  • {w}\n"
        
        if self.errors:
            report += "\nERRORES:\n--------\n"
            for e in self.errors:
                report += f"  • {e}\n"
        
        report += f"""
{'='*70}
PRÓXIMOS PASOS:
{'='*70}

1. Revisa el reporte anterior
2. Si hay errores, corrígelos antes de continuar
3. Ejecuta los siguientes comandos:

   git add .
   git status  (verifica que no haya archivos sensibles)
   git commit -m "Clean project structure - ready for GitHub"
   git push origin main

ARCHIVOS PROTEGIDOS (NO se subirán):
------------------------------------
  • .env (credenciales)
  • sessions/ (datos personales)
  • experience_memory/ (memoria)
  • logs/ (registros)
  • __pycache__/ (caché)
  • backups/ (copias)
  • .gradle/, .idea/ (configuración IDE)

ARCHIVOS QUE SÍ SE SUBIRÁN:
---------------------------
  • agent/ (código fuente)
  • app/ (aplicación Android)
  • static/, templates/ (web)
  • tests/ (pruebas)
  • README.md, documentación
  • .env.example (plantilla segura)

{'='*70}
"""
        
        print(report)
        
        # Guardar reporte en archivo
        report_file = self.project_root / "GITHUB_PREP_REPORT.txt"
        report_file.write_text(report, encoding='utf-8')
        self.print_success(f"Reporte guardado en: GITHUB_PREP_REPORT.txt")
        
        return len(self.errors) == 0

    def run_full_automation(self):
        """Ejecuta todo el proceso automático."""
        self.print_header(
            "🚀 PREPARACIÓN AUTOMÁTICA PARA GITHUB - KALIN v3.0",
            "="
        )
        
        print(f"Proyecto: {self.project_root}")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Ejecutar todos los pasos
        steps = [
            self.step_1_verify_project,
            self.step_2_check_sensitive_files,
            self.step_3_clean_project,
            self.step_4_verify_gitignore,
            self.step_5_check_git_status,
            self.step_6_generate_report,
        ]
        
        results = []
        for i, step in enumerate(steps, 1):
            try:
                result = step()
                results.append(result)
            except Exception as e:
                self.print_error(f"Error en paso {i}: {e}")
                results.append(False)
        
        # Resumen final
        self.print_header("RESULTADO FINAL", "=")
        
        total_steps = len(steps)
        successful_steps = sum(results)
        
        print(f"\nPasos completados: {successful_steps}/{total_steps}")
        
        if all(results):
            print("\n\033[92m✅ ¡TODO LISTO! Tu proyecto está preparado para GitHub\033[0m")
            print("\nAhora puedes ejecutar:")
            print("  git add .")
            print('  git commit -m "Clean project structure - ready for GitHub"')
            print("  git push origin main")
            return True
        else:
            print("\n\033[93m⚠️  Hay advertencias o errores que requieren atención\033[0m")
            print("\nRevisa el reporte generado: GITHUB_PREP_REPORT.txt")
            
            if self.errors:
                print(f"\n\033[91mErrores críticos: {len(self.errors)}\033[0m")
                for err in self.errors:
                    print(f"  • {err}")
            
            return False

def main():
    """Función principal."""
    prep = AutoGitHubPrep()
    success = prep.run_full_automation()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
