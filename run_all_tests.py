"""
Script para ejecutar todos los tests y capturar errores
"""
import subprocess
import sys
from pathlib import Path

def run_test(test_file):
    """Ejecuta un archivo de test y devuelve el resultado"""
    print(f"\n{'='*70}")
    print(f"EJECUTANDO: {test_file}")
    print('='*70)
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos timeout
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return {
            'file': test_file,
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            'file': test_file,
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': 'TIMEOUT: El test tardó más de 5 minutos'
        }
    except Exception as e:
        return {
            'file': test_file,
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': f'ERROR: {str(e)}'
        }

def main():
    """Ejecutar todos los tests"""
    test_files = [
        Path('E:/kalin/test_funcional.py'),
        Path('E:/kalin/test_endpoints.py'),
        Path('E:/kalin/test_llm_providers.py'),
        Path('E:/kalin/test_new_architecture.py'),
        Path('E:/kalin/test_new_components.py'),
    ]
    
    results = []
    
    for test_file in test_files:
        if test_file.exists():
            result = run_test(test_file)
            results.append(result)
        else:
            print(f"⚠️  Archivo no encontrado: {test_file}")
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE TESTS")
    print("="*70)
    
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    
    for result in results:
        status = "✅ PASÓ" if result['success'] else "❌ FALLÓ"
        print(f"{result['file'].name:40} {status}")
    
    print(f"\nTotal: {passed}/{len(results)} tests pasaron")
    print("="*70)
    
    if failed > 0:
        print(f"\n⚠️  {failed} test(s) fallaron. Revisa los errores arriba.")
        return False
    else:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
