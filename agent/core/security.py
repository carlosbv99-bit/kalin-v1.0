"""
Sistema de seguridad para Kalin.
Validación de rutas, lista blanca de archivos y sanitización.
"""

import os
import re
from typing import List, Set, Optional
from pathlib import Path
from agent.core.logger import get_logger

logger = get_logger('kalin.security')

class SecurityManager:
    """Gestiona la seguridad de operaciones de archivos"""
    
    def __init__(self):
        # Lista blanca de extensiones permitidas
        self.allowed_extensions: Set[str] = {
            '.py', '.js', '.ts', '.java', '.kt', '.dart', '.go', '.rs',
            '.c', '.cpp', '.h', '.hpp', '.cs', '.rb', '.php',
            '.html', '.css', '.scss', '.sass', '.less',
            '.json', '.yaml', '.yml', '.xml', '.toml', '.ini',
            '.md', '.txt', '.rst', '.log',
            '.sh', '.bat', '.ps1', '.cmd',
        }
        
        # Extensiones peligrosas (nunca permitir modificación)
        self.dangerous_extensions: Set[str] = {
            '.exe', '.dll', '.so', '.dylib',
            '.pyc', '.pyo', '.pyd',
            '.class', '.jar', '.war',
            '.bak', '.tmp', '.swp',
        }
        
        # Lista negra de patrones de ruta
        self.dangerous_patterns: List[str] = [
            'node_modules',
            '.git',
            '__pycache__',
            '.venv',
            'venv',
            '.idea',
            '.vscode',
            'build',
            'dist',
            'target',
            '.gradle',
        ]
        
        # Directorios protegidos del sistema
        self.protected_directories: List[str] = [
            'C:\\Windows',
            'C:\\Program Files',
            'C:\\Program Files (x86)',
            '/etc',
            '/usr',
            '/var',
            '/root',
        ]
        
        logger.info("SecurityManager initialized")
    
    def is_safe_path(self, file_path: str, project_root: str = None) -> tuple:
        """
        Valida si una ruta es segura para operar.
        Returns: (bool, Optional[str]) - (es_seguro, mensaje_error)
        """
        try:
            # Normalizar ruta
            normalized = os.path.normpath(os.path.abspath(file_path))
            
            # Verificar que no esté en directorios protegidos
            for protected in self.protected_directories:
                if normalized.startswith(protected):
                    return False, f"❌ Ruta en directorio protegido: {protected}"
            
            # Si hay project_root, verificar que esté dentro de él
            if project_root:
                project_normalized = os.path.normpath(os.path.abspath(project_root))
                if not normalized.startswith(project_normalized):
                    return False, "❌ Archivo fuera del directorio del proyecto"
            
            # Verificar patrones peligrosos
            for pattern in self.dangerous_patterns:
                if pattern in normalized:
                    return False, f"❌ Ruta contiene directorio restringido: {pattern}"
            
            # Verificar extensión
            ext = os.path.splitext(normalized)[1].lower()
            
            if ext in self.dangerous_extensions:
                return False, f"❌ Extensión peligrosa no permitida: {ext}"
            
            if ext and ext not in self.allowed_extensions and ext != '':
                logger.warning(f"Unknown extension: {ext}")
                # No bloquear extensiones desconocidas, solo advertir
            
            return True, None
            
        except Exception as e:
            logger.error(f"Path validation error: {e}")
            return False, f"❌ Error validando ruta: {str(e)}"
    
    def sanitize_path(self, path: str) -> str:
        """
        Sanitiza una ruta eliminando caracteres peligrosos.
        """
        # Eliminar null bytes
        path = path.replace('\x00', '')
        
        # Normalizar separadores
        path = os.path.normpath(path)
        
        # Eliminar .. traversal attempts
        path = os.path.abspath(path)
        
        return path
    
    def is_safe_filename(self, filename: str) -> tuple:
        """
        Valida si un nombre de archivo es seguro.
        Returns: (bool, Optional[str])
        """
        # Verificar caracteres peligrosos
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\x00']
        for char in dangerous_chars:
            if char in filename:
                return False, f"❌ Caracter peligroso en nombre: {char}"
        
        # Verificar longitud
        if len(filename) > 255:
            return False, "❌ Nombre de archivo demasiado largo"
        
        # Verificar que no esté vacío
        if not filename.strip():
            return False, "❌ Nombre de archivo vacío"
        
        # Verificar extensiones peligrosas
        ext = os.path.splitext(filename)[1].lower()
        if ext in self.dangerous_extensions:
            return False, f"❌ Extensión peligrosa: {ext}"
        
        return True, None
    
    def validate_code_content(self, code: str, max_length: int = 50000) -> tuple:
        """
        Valida el contenido de código antes de escribirlo.
        Returns: (bool, Optional[str])
        """
        if not code:
            return False, "❌ Código vacío"
        
        if len(code) > max_length:
            return False, f"❌ Código demasiado largo ({len(code)} > {max_length})"
        
        # Verificar que no contenga null bytes
        if '\x00' in code:
            return False, "❌ Código contiene caracteres nulos"
        
        # Verificar patrones sospechosos (comandos de sistema)
        suspicious_patterns = [
            r'os\.system\(',
            r'subprocess\.call\(',
            r'eval\(',
            r'exec\(',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, code):
                logger.warning(f"Suspicious pattern detected: {pattern}")
                # No bloquear, solo advertir en logs
        
        return True, None
    
    def get_file_risk_level(self, file_path: str) -> str:
        """
        Determina el nivel de riesgo de un archivo.
        Returns: 'low', 'medium', 'high'
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        # Archivos de configuración pueden ser sensibles
        if ext in ['.env', '.pem', '.key', '.crt', '.config']:
            return 'high'
        
        # Archivos de código son riesgo medio
        if ext in self.allowed_extensions:
            return 'medium'
        
        # Archivos desconocidos son riesgo alto
        return 'high'
    
    def log_security_event(self, event_type: str, details: str, severity: str = 'info'):
        """Registra un evento de seguridad"""
        if severity == 'warning':
            logger.warning(f"SECURITY [{event_type}]: {details}")
        elif severity == 'error':
            logger.error(f"SECURITY [{event_type}]: {details}")
        else:
            logger.info(f"SECURITY [{event_type}]: {details}")

# Instancia global
security_manager = SecurityManager()
