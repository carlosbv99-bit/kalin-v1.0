"""
Security Hardening para Kalin - Protección contra vulnerabilidades críticas.
Aborda: RCE, fuga de credenciales, plugins maliciosos, exposición pública.
"""

import os
import re
import secrets
import hashlib
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from agent.core.logger import get_logger

logger = get_logger('kalin.security_hardening')

class CredentialManager:
    """Gestiona credenciales de forma segura (nunca en logs o errores)"""
    
    _sensitive_patterns = [
        r'API_KEY',
        r'SECRET',
        r'PASSWORD',
        r'TOKEN',
        r'PRIVATE_KEY',
        r'ACCESS_KEY',
    ]
    
    @staticmethod
    def mask_sensitive_data(text: str) -> str:
        """Enmascara datos sensibles en logs y mensajes"""
        masked = text
        
        for pattern in CredentialManager._sensitive_patterns:
            # Reemplazar valores de variables sensibles
            regex = rf'({pattern}\s*[=:]\s*)(\S+)'
            masked = re.sub(regex, r'\1***MASKED***', masked, flags=re.IGNORECASE)
        
        # Enmascarar tokens de OpenAI/Anthropic
        masked = re.sub(r'sk-[a-zA-Z0-9]{20,}', 'sk-***MASKED***', masked)
        masked = re.sub(r'hf_[a-zA-Z0-9]{20,}', 'hf_***MASKED***', masked)
        
        return masked
    
    @staticmethod
    def validate_env_file(env_path: str) -> Tuple[bool, List[str]]:
        """
        Valida que el archivo .env no tenga credenciales hardcodeadas inseguras.
        Returns: (es_valido, lista_de_errores)
        """
        errors = []
        
        if not os.path.exists(env_path):
            return True, []  # No existe, no hay problema
        
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Ignorar comentarios y líneas vacías
            if not line or line.startswith('#'):
                continue
            
            # Verificar que no haya ejemplos de API keys reales
            if 'sk-proj-' in line or 'sk-ant-' in line or 'hf_' in line:
                if 'xxxx' not in line and 'example' not in line.lower():
                    errors.append(
                        f"Línea {i}: Posible API key real detectada. "
                        f"Usa variables de entorno, no hardcodees claves."
                    )
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_error_message(error_msg: str) -> str:
        """Sanitiza mensajes de error para evitar fuga de credenciales"""
        sanitized = CredentialManager.mask_sensitive_data(error_msg)
        
        # Eliminar paths absolutos del sistema
        sanitized = re.sub(r'[A-Z]:\\[^"]+', '[PATH_REDACTED]', sanitized)
        sanitized = re.sub(r'/home/[^/]+/', '[PATH_REDACTED]', sanitized)
        
        return sanitized

class CommandSanitizer:
    """Previene Remote Code Execution (RCE) sanitizando comandos"""
    
    # Lista negra de comandos peligrosos
    DANGEROUS_COMMANDS = [
        'rm -rf', 'del /f', 'format', 'shutdown', 'reboot',
        'wget', 'curl', 'powershell -enc', 'bash -c',
        'eval', 'exec', 'system', 'popen',
        'chmod 777', 'chown', 'sudo',
        'net user', 'passwd', 'useradd',
        'iptables', 'firewall',
    ]
    
    # Caracteres peligrosos en argumentos
    DANGEROUS_CHARS = [';', '|', '&', '`', '$', '(', ')', '{', '}', '<', '>', '\n', '\r']
    
    @staticmethod
    def is_safe_command(command: str, allowed_commands: List[str] = None) -> Tuple[bool, str]:
        """
        Valida si un comando es seguro de ejecutar.
        Returns: (es_seguro, mensaje_error)
        """
        command_lower = command.lower().strip()
        
        # Verificar lista negra
        for dangerous in CommandSanitizer.DANGEROUS_COMMANDS:
            if dangerous in command_lower:
                return False, f"Comando peligroso detectado: {dangerous}"
        
        # Verificar caracteres peligrosos
        for char in CommandSanitizer.DANGEROUS_CHARS:
            if char in command:
                return False, f"Carácter peligroso detectado: {char}"
        
        # Si hay lista blanca, verificar que esté permitida
        if allowed_commands:
            if command_lower not in [cmd.lower() for cmd in allowed_commands]:
                return False, f"Comando no permitido: {command}"
        
        return True, ""
    
    @staticmethod
    def sanitize_subprocess_args(args: List[str]) -> List[str]:
        """Sanitiza argumentos para subprocess.run"""
        sanitized = []
        
        for arg in args:
            # Eliminar caracteres peligrosos
            clean_arg = arg
            for char in CommandSanitizer.DANGEROUS_CHARS:
                clean_arg = clean_arg.replace(char, '')
            
            # Validar longitud
            if len(clean_arg) > 1000:
                logger.warning(f"Argument too long: {len(clean_arg)} chars")
                raise ValueError("Argumento demasiado largo")
            
            sanitized.append(clean_arg)
        
        return sanitized
    
    @staticmethod
    def safe_run_git_command(command: str, repo_path: str) -> Tuple[bool, str]:
        """
        Ejecuta comandos Git de forma segura.
        Solo permite subcomandos específicos de Git.
        """
        allowed_git_commands = [
            'status', 'log', 'diff', 'branch', 'commit',
            'add', 'push', 'pull', 'fetch', 'merge',
            'checkout', 'stash', 'tag', 'remote'
        ]
        
        # Extraer subcomando
        parts = command.split()
        if len(parts) < 2 or parts[0] != 'git':
            return False, "Comando Git inválido"
        
        git_subcommand = parts[1]
        
        if git_subcommand not in allowed_git_commands:
            return False, f"Subcomando Git no permitido: {git_subcommand}"
        
        # Sanitizar argumentos restantes
        try:
            sanitized_args = CommandSanitizer.sanitize_subprocess_args(parts)
        except ValueError as e:
            return False, str(e)
        
        return True, ' '.join(sanitized_args)

class PluginValidator:
    """Valida plugins antes de cargarlos para prevenir código malicioso"""
    
    # Patrones sospechosos en código de plugins
    SUSPICIOUS_PATTERNS = [
        r'os\.system\s*\(',
        r'subprocess\.(run|call|Popen)\s*\(',
        r'eval\s*\(',
        r'exec\s*\(',
        r'__import__\s*\(',
        r'importlib\.import_module\s*\(',
        r'requests\.(get|post|put|delete)\s*\(',
        r'urllib\.request',
        r'socket\.',
        r'ftplib\.',
        r'smtplib\.',
        r'keyring\.',
        r'getpass\.',
    ]
    
    @staticmethod
    def validate_plugin_code(plugin_path: str) -> Tuple[bool, List[str]]:
        """
        Valida el código de un plugin antes de cargarlo.
        Returns: (es_seguro, lista_de_alertas)
        """
        alerts = []
        
        if not os.path.exists(plugin_path):
            return False, ["Plugin file not found"]
        
        with open(plugin_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Verificar patrones sospechosos
        for pattern in PluginValidator.SUSPICIOUS_PATTERNS:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                alerts.append(
                    f"Línea {line_num}: Patrón sospechoso detectado: {match.group()}. "
                    f"Revisar manualmente antes de cargar."
                )
        
        # Verificar imports externos
        import_pattern = r'^(?:import|from)\s+(\w+)'
        imports = re.findall(import_pattern, code, re.MULTILINE)
        
        dangerous_imports = [
            'os', 'sys', 'subprocess', 'socket', 'requests',
            'urllib', 'ftplib', 'smtplib', 'keyring', 'getpass',
            'ctypes', 'pickle', 'shelve', 'marshal'
        ]
        
        for imp in imports:
            if imp in dangerous_imports:
                alerts.append(f"Import potencialmente peligroso: {imp}")
        
        # Calcular hash del plugin para auditoría
        plugin_hash = hashlib.sha256(code.encode()).hexdigest()
        logger.info(f"Plugin hash: {plugin_hash}")
        
        # Si hay alertas críticas, bloquear carga
        critical_alerts = [a for a in alerts if 'eval' in a or 'exec' in a or 'os.system' in a]
        if critical_alerts:
            return False, critical_alerts
        
        return len(alerts) == 0, alerts
    
    @staticmethod
    def generate_plugin_report(plugin_path: str) -> Dict:
        """Genera reporte de seguridad para un plugin"""
        is_safe, alerts = PluginValidator.validate_plugin_code(plugin_path)
        
        return {
            'plugin': os.path.basename(plugin_path),
            'safe_to_load': is_safe,
            'alerts': alerts,
            'alert_count': len(alerts),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }

class NetworkSecurity:
    """Hardening de configuración de red para prevenir exposición pública"""
    
    @staticmethod
    def validate_server_config(host: str, port: int) -> Tuple[bool, List[str]]:
        """
        Valida configuración del servidor para prevenir exposición accidental.
        """
        warnings = []
        
        # Verificar que no se use 0.0.0.0 por defecto
        if host == '0.0.0.0':
            warnings.append(
                "⚠️ ADVERTENCIA: Servidor configurado en 0.0.0.0 (todas las interfaces). "
                "Esto expone el servidor a internet. Usa 127.0.0.1 para desarrollo local."
            )
        
        # Verificar puertos comunes expuestos
        exposed_ports = [80, 443, 8080, 5000, 8000]
        if port in exposed_ports:
            warnings.append(
                f"⚠️ Puerto {port} es comúnmente escaneado. "
                f"Asegúrate de usar firewall y autenticación."
            )
        
        # Verificar que debug esté desactivado en producción
        if os.getenv('FLASK_DEBUG', '0').lower() == '1':
            if os.getenv('KALIN_MODE', 'development').lower() == 'production':
                warnings.append(
                    "❌ CRÍTICO: Flask DEBUG activado en modo producción. "
                    "Esto permite ejecución remota de código."
                )
        
        return len(warnings) == 0, warnings
    
    @staticmethod
    def generate_security_headers() -> Dict[str, str]:
        """Genera headers de seguridad HTTP"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
        }

class SecurityAuditor:
    """Auditor de seguridad completo para Kalin"""
    
    def __init__(self):
        self.credential_manager = CredentialManager()
        self.command_sanitizer = CommandSanitizer()
        self.plugin_validator = PluginValidator()
        self.network_security = NetworkSecurity()
    
    def run_full_audit(self) -> Dict:
        """Ejecuta auditoría de seguridad completa"""
        logger.info("Starting full security audit...")
        
        results = {
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'checks': {}
        }
        
        # 1. Verificar archivo .env
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '.env')
        env_valid, env_errors = self.credential_manager.validate_env_file(env_path)
        results['checks']['env_security'] = {
            'passed': env_valid,
            'errors': env_errors
        }
        
        # 2. Verificar configuración de red
        host = os.getenv('FLASK_HOST', '127.0.0.1')
        port = int(os.getenv('FLASK_PORT', '5000'))
        network_valid, network_warnings = self.network_security.validate_server_config(host, port)
        results['checks']['network_security'] = {
            'passed': network_valid,
            'warnings': network_warnings
        }
        
        # 3. Verificar plugins instalados
        plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'plugins')
        plugin_reports = []
        
        if os.path.exists(plugins_dir):
            for plugin_file in os.listdir(plugins_dir):
                if plugin_file.endswith('.py'):
                    plugin_path = os.path.join(plugins_dir, plugin_file)
                    report = self.plugin_validator.generate_plugin_report(plugin_path)
                    plugin_reports.append(report)
        
        results['checks']['plugins'] = {
            'total_plugins': len(plugin_reports),
            'reports': plugin_reports
        }
        
        # 4. Verificar subprocess usage
        results['checks']['subprocess_safety'] = {
            'note': 'All subprocess calls should use shell=False and validated arguments'
        }
        
        # Resumen
        total_checks = len(results['checks'])
        passed_checks = sum(1 for check in results['checks'].values() if check.get('passed', True))
        
        results['summary'] = {
            'total_checks': total_checks,
            'passed': passed_checks,
            'failed': total_checks - passed_checks,
            'security_score': f"{(passed_checks/total_checks*100):.1f}%"
        }
        
        logger.info(f"Security audit completed: {results['summary']['security_score']}")
        
        return results

# Instancia global
security_auditor = SecurityAuditor()
