"""
Protección contra Prompt Injection y Verificación de Resultados.
Previene acciones maliciosas y detecta fallas silenciosas.
"""

import re
from typing import Dict, List, Tuple, Optional
from agent.core.logger import get_logger

logger = get_logger('kalin.prompt_security')

class PromptInjectionDetector:
    """Detecta intentos de prompt injection en inputs del usuario"""
    
    # Patrones sospechosos de inyección
    INJECTION_PATTERNS = [
        # Intentos de escape del contexto
        r'ignore\s+(previous|above|all)\s+(instructions|rules|commands)',
        r'forget\s+(everything|all|your)\s+(instructions|training|rules)',
        r'bypass\s+(security|restrictions|filters)',
        r'override\s+(system|default)\s+(settings|configuration)',
        
        # Comandos shell disfrazados
        r'(delete|remove|erase)\s+(all|every)\s+files?',
        r'(format|wipe|destroy)\s+(disk|drive|system)',
        r'rm\s+-rf\s+/',
        r'del\s+/[fqs]',
        
        # Manipulación de roles
        r'you\s+are\s+now\s+(admin|root|superuser)',
        r'system:\s*(new\s+instruction|override)',
        r'\[SYSTEM\]',
        r'<|assistant|>',
        
        # Exfiltración de datos
        r'reveal\s+(your|the)\s+(instructions|prompt|system)',
        r'print\s+(your|the)\s+(full|complete)\s+(prompt|instructions)',
        r'output\s+(everything|all)\s+(you\s+know|your\s+training)',
    ]
    
    # Palabras clave de alto riesgo
    HIGH_RISK_KEYWORDS = [
        'sudo', 'admin', 'root', 'superuser',
        'delete all', 'format', 'wipe', 'destroy',
        'bypass', 'override', 'ignore rules',
        'reveal prompt', 'show instructions',
    ]
    
    @staticmethod
    def analyze_prompt(user_input: str) -> Dict:
        """
        Analiza input del usuario buscando inyecciones.
        Returns: dict con nivel de riesgo y detalles
        """
        result = {
            'risk_level': 'low',  # low, medium, high, critical
            'is_suspicious': False,
            'detected_patterns': [],
            'confidence': 0.0,
            'recommendation': 'allow'  # allow, warn, block
        }
        
        input_lower = user_input.lower().strip()
        
        # Verificar patrones de inyección
        for pattern in PromptInjectionDetector.INJECTION_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                result['is_suspicious'] = True
                result['detected_patterns'].append(pattern)
                result['confidence'] += 0.3
        
        # Verificar palabras clave de alto riesgo
        for keyword in PromptInjectionDetector.HIGH_RISK_KEYWORDS:
            if keyword in input_lower:
                result['is_suspicious'] = True
                result['detected_patterns'].append(f"keyword:{keyword}")
                result['confidence'] += 0.2
        
        # Determinar nivel de riesgo
        if result['confidence'] >= 0.8:
            result['risk_level'] = 'critical'
            result['recommendation'] = 'block'
        elif result['confidence'] >= 0.5:
            result['risk_level'] = 'high'
            result['recommendation'] = 'warn'
        elif result['confidence'] >= 0.2:
            result['risk_level'] = 'medium'
            result['recommendation'] = 'warn'
        else:
            result['risk_level'] = 'low'
            result['recommendation'] = 'allow'
        
        if result['is_suspicious']:
            logger.warning(
                f"Suspicious prompt detected (risk={result['risk_level']}): "
                f"{user_input[:100]}"
            )
        
        return result
    
    @staticmethod
    def sanitize_prompt(user_input: str) -> str:
        """
        Sanitiza el prompt eliminando posibles inyecciones.
        """
        sanitized = user_input
        
        # Eliminar etiquetas de sistema
        sanitized = re.sub(r'\[SYSTEM\]|\[USER\]|\[ASSISTANT\]', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'<\|.*?\|>', '', sanitized)
        
        # Limitar longitud para prevenir ataques de buffer
        if len(sanitized) > 10000:
            logger.warning(f"Prompt too long: {len(sanitized)} chars, truncating")
            sanitized = sanitized[:10000]
        
        return sanitized.strip()

class ResultVerifier:
    """Verifica que los resultados del agente sean completos y correctos"""
    
    @staticmethod
    def verify_code_fix(original_code: str, fixed_code: str, intention: str) -> Dict:
        """
        Verifica que un fix de código sea válido y completo.
        """
        verification = {
            'is_valid': True,
            'completeness': 100.0,
            'issues': [],
            'warnings': []
        }
        
        # 1. Verificar que el código no esté vacío
        if not fixed_code or len(fixed_code.strip()) < 10:
            verification['is_valid'] = False
            verification['issues'].append("Código generado está vacío o incompleto")
            return verification
        
        # 2. Verificar sintaxis
        try:
            compile(fixed_code, '<string>', 'exec')
        except SyntaxError as e:
            verification['is_valid'] = False
            verification['issues'].append(f"Error de sintaxis: {str(e)}")
            return verification
        
        # 3. Verificar que no se perdió contenido crítico
        original_lines = len(original_code.split('\n'))
        fixed_lines = len(fixed_code.split('\n'))
        
        if fixed_lines < original_lines * 0.5:
            verification['warnings'].append(
                f"Código reducido significativamente: {original_lines} → {fixed_lines} líneas"
            )
            verification['completeness'] = (fixed_lines / original_lines) * 100
        
        # 4. Verificar que funciones/métodos importantes existen
        original_functions = ResultVerifier._extract_functions(original_code)
        fixed_functions = ResultVerifier._extract_functions(fixed_code)
        
        missing_functions = original_functions - fixed_functions
        if missing_functions:
            verification['warnings'].append(
                f"Funciones perdidas: {', '.join(missing_functions)}"
            )
        
        # 5. Verificar imports críticos
        original_imports = ResultVerifier._extract_imports(original_code)
        fixed_imports = ResultVerifier._extract_imports(fixed_code)
        
        missing_imports = original_imports - fixed_imports
        if missing_imports:
            verification['warnings'].append(
                f"Imports perdidos: {', '.join(missing_imports)}"
            )
        
        return verification
    
    @staticmethod
    def verify_task_completion(task_type: str, result: Dict) -> Dict:
        """
        Verifica que una tarea se completó correctamente.
        """
        verification = {
            'completed': False,
            'partial': False,
            'errors': [],
            'quality_score': 0.0
        }
        
        if task_type == 'fix':
            # Verificar fix de código
            if not result.get('preview', '').strip():
                verification['errors'].append("FAIL")
            elif 'preview' not in result or not result.get('preview'):
                verification['errors'].append("No hay preview del código fixeado")
            elif len(result['preview']) < 50:
                verification['partial'] = True
                verification['errors'].append("Preview muy corto - posible fix incompleto")
            else:
                verification['completed'] = True
                verification['quality_score'] = min(100, len(result['preview']) / 10)
        
        elif task_type == 'analyze':
            # Verificar análisis
            if 'respuesta' not in result or len(result['respuesta']) < 100:
                verification['partial'] = True
                verification['errors'].append("Análisis muy breve - posiblemente incompleto")
            else:
                verification['completed'] = True
                verification['quality_score'] = min(100, len(result['respuesta']) / 5)
        
        elif task_type == 'scan':
            # Verificar scan de proyecto
            if 'data' not in result:
                verification['errors'].append("Scan no retornó datos")
            elif result['data'].get('total_archivos', 0) == 0:
                verification['partial'] = True
                verification['warnings'].append("No se encontraron archivos")
            else:
                verification['completed'] = True
                verification['quality_score'] = 100.0
        
        return verification
    
    @staticmethod
    def _extract_functions(code: str) -> set:
        """Extrae nombres de funciones del código"""
        import re
        pattern = r'def\s+(\w+)\s*\('
        return set(re.findall(pattern, code))
    
    @staticmethod
    def _extract_imports(code: str) -> set:
        """Extrae módulos importados"""
        import re
        imports = set()
        
        # import X
        for match in re.finditer(r'^import\s+(\w+)', code, re.MULTILINE):
            imports.add(match.group(1))
        
        # from X import Y
        for match in re.finditer(r'^from\s+(\w+)', code, re.MULTILINE):
            imports.add(match.group(1))
        
        return imports

class ActionGuardian:
    """Guardián que previene acciones peligrosas o involuntarias"""
    
    # Acciones que requieren confirmación explícita
    REQUIRES_CONFIRMATION = [
        'delete', 'remove', 'erase', 'format',
        'overwrite', 'replace_all',
        'execute_shell', 'run_command',
    ]
    
    # Acciones bloqueadas completamente
    BLOCKED_ACTIONS = [
        'format_disk', 'wipe_system', 'delete_os',
        'modify_bootloader', 'change_root_password',
    ]
    
    @staticmethod
    def validate_action(action: str, params: Dict) -> Tuple[bool, str]:
        """
        Valida si una acción es segura de ejecutar.
        Returns: (es_seguro, mensaje)
        """
        action_lower = action.lower()
        
        # Verificar acciones bloqueadas
        for blocked in ActionGuardian.BLOCKED_ACTIONS:
            if blocked in action_lower:
                return False, f"❌ Acción bloqueada por seguridad: {action}"
        
        # Verificar acciones que requieren confirmación
        for requires_conf in ActionGuardian.REQUIRES_CONFIRMATION:
            if requires_conf in action_lower:
                return False, f"⚠️ Acción requiere confirmación manual: {action}"
        
        # Verificar parámetros peligrosos
        if 'path' in params:
            path = params['path']
            
            # Prevenir acceso a directorios del sistema
            system_paths = ['/etc', '/usr', '/var', 'C:\\Windows', 'C:\\Program Files']
            for sys_path in system_paths:
                if path.startswith(sys_path):
                    return False, f"❌ Acceso denegado a ruta del sistema: {path}"
        
        return True, "Acción aprobada"
    
    @staticmethod
    def require_confirmation(message: str) -> bool:
        """
        Solicita confirmación al usuario para acciones riesgosas.
        En producción, esto mostraría un diálogo UI.
        """
        logger.info(f"Confirmation required: {message}")
        # Por ahora, auto-aprobar en modo desarrollo
        # En producción, implementar UI de confirmación
        return True

# Instancias globales
prompt_detector = PromptInjectionDetector()
result_verifier = ResultVerifier()
action_guardian = ActionGuardian()
