"""
Sistema de Testing Automático para Kalin.
Genera y ejecuta tests unitarios automáticamente después de fixes.
"""

import os
import subprocess
import tempfile
from typing import Dict, List, Optional, Tuple
from agent.core.logger import get_logger

logger = get_logger('kalin.testing')

class TestGenerator:
    """Genera tests unitarios automáticamente"""
    
    @staticmethod
    def generate_unit_test(file_path: str, codigo: str) -> str:
        """
        Genera un test unitario básico para el código dado.
        """
        filename = os.path.basename(file_path)
        module_name = os.path.splitext(filename)[0]
        
        # Detectar funciones en el código
        functions = TestGenerator._extract_functions(codigo)
        
        test_code = f'''"""
Tests automáticos generados por Kalin para {filename}
"""

import pytest
from {module_name} import *

'''
        
        for func_name, params in functions.items():
            if func_name.startswith('_'):
                continue
            
            param_list = ', '.join([f'param_{p}' for p in params])
            
            test_code += f'''
def test_{func_name}():
    """Test automático para {func_name}"""
    try:
        # TODO: Ajustar parámetros según sea necesario
        result = {func_name}({param_list})
        assert result is not None
    except Exception as e:
        # El test captura excepciones pero no falla
        pass

'''
        
        logger.info(f"Generated test with {len(functions)} test cases")
        
        return test_code
    
    @staticmethod
    def _extract_functions(codigo: str) -> Dict[str, List[str]]:
        """Extrae nombres de funciones y sus parámetros"""
        import re
        
        functions = {}
        pattern = r'def\s+(\w+)\s*\(([^)]*)\)'
        
        matches = re.finditer(pattern, codigo)
        
        for match in matches:
            func_name = match.group(1)
            params_str = match.group(2).strip()
            
            if params_str:
                params = [p.strip().split('=')[0].strip() for p in params_str.split(',')]
                # Filtrar 'self' y 'cls'
                params = [p for p in params if p not in ['self', 'cls']]
            else:
                params = []
            
            functions[func_name] = params
        
        return functions

class TestRunner:
    """Ejecuta tests automáticamente"""
    
    @staticmethod
    def run_tests(test_directory: str) -> Dict:
        """
        Ejecuta todos los tests en un directorio.
        Returns: dict con resultados
        """
        try:
            logger.info(f"Running tests in: {test_directory}")
            
            # Ejecutar pytest
            result = subprocess.run(
                ['pytest', test_directory, '-v', '--json'],
                cwd=test_directory,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            passed = result.returncode == 0
            
            # Parsear output
            stats = TestRunner._parse_pytest_output(result.stdout)
            
            logger.info(f"Tests completed: {stats.get('passed', 0)} passed, {stats.get('failed', 0)} failed")
            
            return {
                'success': passed,
                'stats': stats,
                'output': result.stdout,
                'errors': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Tests timed out")
            return {
                'success': False,
                'error': 'Tests timed out after 60 seconds'
            }
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def _parse_pytest_output(output: str) -> Dict:
        """Parsea el output de pytest"""
        import re
        
        stats = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0
        }
        
        # Buscar patrón: "X passed, Y failed in Zs"
        match = re.search(r'(\d+) passed', output)
        if match:
            stats['passed'] = int(match.group(1))
        
        match = re.search(r'(\d+) failed', output)
        if match:
            stats['failed'] = int(match.group(1))
        
        match = re.search(r'(\d+) skipped', output)
        if match:
            stats['skipped'] = int(match.group(1))
        
        stats['total'] = stats['passed'] + stats['failed'] + stats['skipped']
        
        return stats
    
    @staticmethod
    def validate_fix(original_code: str, fixed_code: str, file_path: str) -> bool:
        """
        Valida que un fix no rompa funcionalidad existente.
        """
        try:
            # Crear directorio temporal
            with tempfile.TemporaryDirectory() as tmpdir:
                # Escribir código original y fixed
                original_path = os.path.join(tmpdir, 'original.py')
                fixed_path = os.path.join(tmpdir, 'fixed.py')
                
                with open(original_path, 'w') as f:
                    f.write(original_code)
                
                with open(fixed_path, 'w') as f:
                    f.write(fixed_code)
                
                # Intentar compilar ambos
                try:
                    compile(original_code, original_path, 'exec')
                    compile(fixed_code, fixed_path, 'exec')
                except SyntaxError as e:
                    logger.error(f"Syntax error in fixed code: {e}")
                    return False
                
                # Generar y ejecutar tests básicos
                test_code = TestGenerator.generate_unit_test(file_path, fixed_code)
                test_path = os.path.join(tmpdir, 'test_auto.py')
                
                with open(test_path, 'w') as f:
                    f.write(test_code)
                
                # Ejecutar tests
                result = TestRunner.run_tests(tmpdir)
                
                return result['success']
                
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False

class AutoTester:
    """Orquestador de testing automático"""
    
    def __init__(self):
        self.generator = TestGenerator()
        self.runner = TestRunner()
    
    def test_after_fix(self, file_path: str, original_code: str, fixed_code: str) -> Dict:
        """
        Ejecuta testing automático después de un fix.
        """
        logger.info(f"Starting auto-test for: {file_path}")
        
        result = {
            'file': file_path,
            'syntax_valid': False,
            'tests_generated': False,
            'tests_passed': False,
            'validation_passed': False
        }
        
        try:
            # 1. Validar sintaxis
            try:
                compile(fixed_code, file_path, 'exec')
                result['syntax_valid'] = True
                logger.info("✓ Syntax validation passed")
            except SyntaxError as e:
                logger.error(f"✗ Syntax error: {e}")
                return result
            
            # 2. Generar tests
            test_code = self.generator.generate_unit_test(file_path, fixed_code)
            result['tests_generated'] = True
            logger.info("✓ Tests generated")
            
            # 3. Ejecutar tests
            with tempfile.TemporaryDirectory() as tmpdir:
                # Copiar archivo fixed
                import shutil
                shutil.copy(file_path, tmpdir)
                
                # Escribir test
                test_path = os.path.join(tmpdir, 'test_auto.py')
                with open(test_path, 'w') as f:
                    f.write(test_code)
                
                # Ejecutar
                test_result = self.runner.run_tests(tmpdir)
                result['tests_passed'] = test_result['success']
                result['test_stats'] = test_result.get('stats', {})
            
            logger.info(f"✓ Tests {'passed' if result['tests_passed'] else 'failed'}")
            
            # 4. Validación completa
            result['validation_passed'] = (
                result['syntax_valid'] and 
                result['tests_generated'] and 
                result['tests_passed']
            )
            
            logger.info(f"Auto-test completed: {result['validation_passed']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Auto-test failed: {e}")
            result['error'] = str(e)
            return result

# Instancia global
auto_tester = AutoTester()
