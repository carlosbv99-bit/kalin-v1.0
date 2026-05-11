#!/usr/bin/env python3
"""
Kalin - Ejecutor Completo de Tests
===================================
Ejecuta todos los tests con opciones avanzadas.

Uso:
    python run_all_tests.py [opciones]

Opciones:
    --unit          Solo tests unitarios
    --coverage      Generar reporte de cobertura
    --verbose       Modo verbose
    --html-report   Generar reporte HTML
"""

import subprocess
import sys
import os
from pathlib import Path


def print_header(text):
    """Imprime header formateado"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def run_command(cmd, description):
    """Ejecuta comando y muestra resultado"""
    print(f"🔄 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=False)
    
    if result.returncode == 0:
        print(f"✅ {description} - ÉXITO\n")
        return True
    else:
        print(f"❌ {description} - FALLÓ\n")
        return False


def check_dependencies():
    """Verifica que las dependencias de testing estén instaladas"""
    print("📦 Verificando dependencias de testing...")
    
    required_packages = ['pytest', 'pytest-cov']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"⚠️ Paquetes faltantes: {', '.join(missing)}")
        print("Instalando...")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing)
        print("✅ Dependencias instaladas\n")
    else:
        print("✅ Todas las dependencias presentes\n")


def run_unit_tests(verbose=False):
    """Ejecuta tests unitarios"""
    cmd = f"{sys.executable} -m pytest tests/test_patch_manager.py tests/test_orchestration_layer.py tests/test_memory_manager.py"
    
    if verbose:
        cmd += " -vv"
    
    return run_command(cmd, "Ejecutando tests unitarios")


def run_coverage():
    """Ejecuta tests con cobertura"""
    cmd = f"{sys.executable} -m pytest tests/ --cov=agent --cov-report=term-missing --cov-report=html"
    
    return run_command(cmd, "Generando reporte de cobertura")


def run_specific_test(test_file):
    """Ejecuta un test específico"""
    test_path = Path('tests') / test_file
    
    if not test_path.exists():
        print(f"❌ Test file no encontrado: {test_file}")
        return False
    
    cmd = f"{sys.executable} -m pytest {test_path} -v"
    
    return run_command(cmd, f"Ejecutando {test_file}")


def show_coverage_report():
    """Muestra reporte de cobertura"""
    coverage_html = Path('htmlcov/index.html')
    
    if coverage_html.exists():
        print(f"📊 Reporte de cobertura generado en: {coverage_html.absolute()}")
        
        # Intentar abrir en navegador
        if sys.platform == 'win32':
            os.startfile(str(coverage_html))
        elif sys.platform == 'darwin':
            subprocess.run(['open', str(coverage_html)])
        else:
            subprocess.run(['xdg-open', str(coverage_html)])
    else:
        print("⚠️ No se encontró reporte de cobertura")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Ejecuta tests de Kalin AI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--unit', action='store_true',
                       help='Solo tests unitarios')
    parser.add_argument('--coverage', action='store_true',
                       help='Generar reporte de cobertura')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Modo verbose')
    parser.add_argument('--html-report', action='store_true',
                       help='Generar reporte HTML')
    parser.add_argument('--test', type=str,
                       help='Ejecutar test específico (ej: test_patch_manager.py)')
    
    args = parser.parse_args()
    
    print_header("KALIN AI - TEST RUNNER")
    
    # Verificar dependencias
    check_dependencies()
    
    success = True
    
    if args.test:
        # Ejecutar test específico
        success = run_specific_test(args.test)
    
    elif args.unit:
        # Solo tests unitarios
        success = run_unit_tests(verbose=args.verbose)
    
    elif args.coverage:
        # Tests con cobertura
        success = run_coverage()
        
        if args.html_report:
            show_coverage_report()
    
    else:
        # Ejecutar todo
        print("🚀 Ejecutando suite completa de tests...\n")
        
        # 1. Tests unitarios
        unit_success = run_unit_tests(verbose=args.verbose)
        
        # 2. Cobertura
        if unit_success:
            coverage_success = run_coverage()
            
            if coverage_success and args.html_report:
                show_coverage_report()
            
            success = coverage_success
        else:
            success = False
    
    # Resumen final
    print_header("RESUMEN")
    
    if success:
        print("✅ TODOS LOS TESTS PASARON")
        print("\nPróximos pasos:")
        print("  - Revisa el reporte de cobertura (si se generó)")
        print("  - Commit y push de los cambios")
        print("  - GitHub Actions ejecutará los tests automáticamente")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("\nRevisa los errores arriba y corrige antes de continuar.")
    
    print()
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
