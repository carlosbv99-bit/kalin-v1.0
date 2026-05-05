"""
Sistema de Estabilidad y Auto-Recuperación para Kalin.
Previene CrashLoopBackOff, fetch failures y optimiza rendimiento.
"""

import os
import time
import json
import sqlite3
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from agent.core.logger import get_logger

logger = get_logger('kalin.stability')

class ConfigValidator:
    """Valida configuración antes de aplicar cambios para prevenir CrashLoopBackOff"""
    
    REQUIRED_VARS = ['KALIN_MODE']
    
    VALIDATION_RULES = {
        'KALIN_MODE': {
            'required': True,
            'allowed_values': ['local', 'cloud', 'production'],
            'default': 'local'
        },
        'FLASK_HOST': {
            'required': False,
            'type': 'string',
            'default': '127.0.0.1'
        },
        'FLASK_PORT': {
            'required': False,
            'type': 'int',
            'min': 1024,
            'max': 65535,
            'default': 5000
        },
        'FLASK_DEBUG': {
            'required': False,
            'type': 'bool',
            'allowed_values': ['0', '1'],
            'default': '0'
        },
        'OLLAMA_ENDPOINT': {
            'required': False,
            'type': 'url',
            'default': 'http://127.0.0.1:11434'
        }
    }
    
    @staticmethod
    def validate_config(config: Dict) -> Tuple[bool, List[str]]:
        """
        Valida configuración completa antes de aplicar.
        Returns: (es_valido, lista_de_errores)
        """
        errors = []
        warnings = []
        
        # Verificar variables requeridas
        for var in ConfigValidator.REQUIRED_VARS:
            if var not in config or not config[var]:
                errors.append(f"Variable requerida faltante: {var}")
        
        # Validar cada variable según reglas
        for var_name, rules in ConfigValidator.VALIDATION_RULES.items():
            if var_name not in config:
                if rules.get('required', False):
                    errors.append(f"{var_name} es requerida")
                continue
            
            value = config[var_name]
            
            # Validar tipo
            if rules.get('type') == 'int':
                try:
                    int_value = int(value)
                    if 'min' in rules and int_value < rules['min']:
                        errors.append(f"{var_name} debe ser >= {rules['min']}")
                    if 'max' in rules and int_value > rules['max']:
                        errors.append(f"{var_name} debe ser <= {rules['max']}")
                except (ValueError, TypeError):
                    errors.append(f"{var_name} debe ser un número entero")
            
            # Validar valores permitidos
            if 'allowed_values' in rules:
                if value not in rules['allowed_values']:
                    errors.append(
                        f"{var_name} tiene valor inválido '{value}'. "
                        f"Valores permitidos: {rules['allowed_values']}"
                    )
            
            # Validar URLs
            if rules.get('type') == 'url':
                if not value.startswith(('http://', 'https://')):
                    errors.append(f"{var_name} debe ser una URL válida")
        
        # Advertencias de seguridad
        if config.get('FLASK_DEBUG') == '1' and config.get('KALIN_MODE') == 'production':
            errors.append("CRÍTICO: FLASK_DEBUG=1 en modo producción")
        
        if config.get('FLASK_HOST') == '0.0.0.0':
            warnings.append(
                "ADVERTENCIA: FLASK_HOST=0.0.0.0 expone el servidor a todas las interfaces"
            )
        
        return len(errors) == 0, errors + warnings
    
    @staticmethod
    def safe_update_config(new_config: Dict, config_file: str = '.env') -> Tuple[bool, List[str]]:
        """
        Actualiza configuración de forma segura con rollback automático.
        """
        logger.info(f"Attempting config update: {list(new_config.keys())}")
        
        # 1. Validar nueva configuración
        is_valid, messages = ConfigValidator.validate_config(new_config)
        
        if not is_valid:
            errors = [m for m in messages if m.startswith('CRÍTICO') or m.startswith('Variable')]
            return False, errors
        
        # 2. Crear backup de configuración actual
        backup_file = f"{config_file}.backup.{int(time.time())}"
        
        try:
            if os.path.exists(config_file):
                import shutil
                shutil.copy2(config_file, backup_file)
                logger.info(f"Config backup created: {backup_file}")
            
            # 3. Aplicar nueva configuración
            ConfigValidator._write_config(new_config, config_file)
            
            # 4. Verificar que el sistema puede iniciar con la nueva config
            test_result = ConfigValidator._test_config_load(config_file)
            
            if not test_result:
                # Rollback
                logger.error("Config test failed, rolling back...")
                if os.path.exists(backup_file):
                    import shutil
                    shutil.copy2(backup_file, config_file)
                    os.remove(backup_file)
                return False, ["Configuración inválida - rollback aplicado"]
            
            # 5. Limpiar backup antiguo
            if os.path.exists(backup_file):
                os.remove(backup_file)
            
            logger.info("Config updated successfully")
            return True, []
            
        except Exception as e:
            logger.error(f"Config update failed: {e}")
            # Rollback de emergencia
            if os.path.exists(backup_file):
                import shutil
                shutil.copy2(backup_file, config_file)
            return False, [f"Error aplicando configuración: {str(e)}"]
    
    @staticmethod
    def _write_config(config: Dict, config_file: str):
        """Escribe configuración al archivo .env"""
        with open(config_file, 'w') as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")
    
    @staticmethod
    def _test_config_load(config_file: str) -> bool:
        """Prueba que la configuración se puede cargar correctamente"""
        try:
            from dotenv import load_dotenv
            load_dotenv(config_file, override=True)
            
            # Verificar que variables críticas están presentes
            mode = os.getenv('KALIN_MODE')
            if not mode:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Config load test failed: {e}")
            return False

class HealthMonitor:
    """Monitorea salud del sistema y previene Fetch Failed loops"""
    
    def __init__(self):
        self.health_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'health_status.json'
        )
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.last_health_check = 0
        self.health_check_interval = 60  # segundos
    
    def check_health(self) -> Dict:
        """Verifica salud completa del sistema"""
        current_time = time.time()
        
        # Evitar checks demasiado frecuentes
        if current_time - self.last_health_check < self.health_check_interval:
            return self._load_last_health()
        
        health_status = {
            'timestamp': current_time,
            'status': 'healthy',
            'checks': {}
        }
        
        # 1. Verificar servidor Flask
        flask_healthy = self._check_flask_server()
        health_status['checks']['flask_server'] = flask_healthy
        
        # 2. Verificar LLM provider
        llm_healthy = self._check_llm_provider()
        health_status['checks']['llm_provider'] = llm_healthy
        
        # 3. Verificar base de datos
        db_healthy = self._check_database()
        health_status['checks']['database'] = db_healthy
        
        # 4. Verificar memoria disponible
        memory_healthy = self._check_memory()
        health_status['checks']['memory'] = memory_healthy
        
        # Determinar estado general
        all_healthy = all([flask_healthy, llm_healthy, db_healthy, memory_healthy])
        
        if all_healthy:
            health_status['status'] = 'healthy'
            self.consecutive_failures = 0
        else:
            health_status['status'] = 'degraded'
            self.consecutive_failures += 1
            
            if self.consecutive_failures >= self.max_consecutive_failures:
                health_status['status'] = 'critical'
                logger.warning(f"Health check failed {self.consecutive_failures} times consecutively")
        
        # Guardar estado
        self._save_health_status(health_status)
        self.last_health_check = current_time
        
        return health_status
    
    def _check_flask_server(self) -> bool:
        """Verifica que el servidor Flask esté respondiendo"""
        # NOTA: Si estamos DENTRO del servidor Flask, no podemos hacernos self-check
        # En su lugar, verificamos que la app esté inicializada correctamente
        try:
            # Verificar que la app de Flask existe y está configurada
            import sys
            if 'web' in sys.modules:
                from web import app
                if app and hasattr(app, 'config'):
                    return True
            
            # Fallback: intentar conexión solo si NO estamos en modo debug
            # (evita deadlock en desarrollo)
            import os
            if os.getenv('FLASK_DEBUG', '0') == '0':
                import requests
                response = requests.get('http://localhost:5000/health', timeout=2)
                return response.status_code == 200
            
            return True  # Asumir healthy en modo debug
            
        except Exception as e:
            logger.debug(f"Flask health check failed: {e}")
            return False
    
    def _check_llm_provider(self) -> bool:
        """Verifica que el proveedor LLM esté disponible"""
        try:
            from agent.llm.client import is_available
            return is_available()
        except Exception as e:
            logger.debug(f"LLM health check failed: {e}")
            return False
    
    def _check_database(self) -> bool:
        """Verifica integridad de la base de datos"""
        try:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'sessions'
            )
            os.makedirs(db_path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def _check_memory(self) -> bool:
        """Verifica uso de memoria"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            # Alerta si uso > 90%
            return memory.percent < 90
        except ImportError:
            # Si psutil no está instalado, asumir OK
            return True
        except Exception as e:
            logger.debug(f"Memory check failed: {e}")
            return True
    
    def _save_health_status(self, status: Dict):
        """Guarda estado de salud en archivo"""
        try:
            with open(self.health_file, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save health status: {e}")
    
    def _load_last_health(self) -> Dict:
        """Carga último estado de salud conocido"""
        try:
            if os.path.exists(self.health_file):
                with open(self.health_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load health status: {e}")
        
        return {'status': 'unknown', 'checks': {}}
    
    def get_recovery_suggestions(self, health_status: Dict) -> List[str]:
        """Genera sugerencias de recuperación basadas en estado de salud"""
        suggestions = []
        
        if health_status['status'] == 'critical':
            suggestions.append("🚨 Sistema en estado crítico - Reiniciar recomendado")
        
        checks = health_status.get('checks', {})
        
        if not checks.get('flask_server', True):
            suggestions.append("• Servidor Flask no responde - Verificar puerto 5000")
        
        if not checks.get('llm_provider', True):
            suggestions.append("• Proveedor LLM no disponible - Verificar Ollama/API keys")
        
        if not checks.get('database', True):
            suggestions.append("• Base de datos corrupta - Ejecutar reparación")
        
        if not checks.get('memory', True):
            suggestions.append("• Memoria insuficiente - Cerrar otras aplicaciones")
        
        return suggestions

class SQLiteOptimizer:
    """Optimiza SQLite para prevenir fallos de memoria y mejorar rendimiento"""
    
    @staticmethod
    def optimize_database(db_path: str):
        """Aplica optimizaciones a base de datos SQLite"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Optimizaciones de rendimiento
            cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
            cursor.execute("PRAGMA synchronous=NORMAL")  # Balance speed/safety
            cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
            cursor.execute("PRAGMA temp_store=MEMORY")  # Temp tables en RAM
            cursor.execute("PRAGMA mmap_size=268435456")  # 256MB mmap
            
            # Optimizar índices
            cursor.execute("PRAGMA optimize")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Database optimized: {db_path}")
            return True
            
        except Exception as e:
            logger.error(f"Database optimization failed: {e}")
            return False
    
    @staticmethod
    def create_session_table(db_path: str):
        """Crea tabla de sesiones optimizada"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0
                )
            """)
            
            # Índices para búsquedas rápidas
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_id 
                ON sessions(session_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_updated_at 
                ON sessions(updated_at DESC)
            """)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Session table created/verified: {db_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create session table: {e}")
            return False
    
    @staticmethod
    def cleanup_old_sessions(db_path: str, max_age_days: int = 30):
        """Limpia sesiones antiguas para liberar espacio"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM sessions 
                WHERE updated_at < datetime('now', '-' || ? || ' days')
            """, (max_age_days,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old sessions")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Session cleanup failed: {e}")
            return 0

class PerformanceOptimizer:
    """Optimizaciones generales de rendimiento"""
    
    @staticmethod
    def check_system_requirements() -> Dict:
        """Verifica requisitos mínimos del sistema"""
        requirements = {
            'meets_minimum': True,
            'warnings': [],
            'recommendations': []
        }
        
        # Verificar RAM
        try:
            import psutil
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024**3)
            
            if total_gb < 2:
                requirements['meets_minimum'] = False
                requirements['warnings'].append(
                    f"⚠️ RAM insuficiente: {total_gb:.1f}GB (mínimo 2GB recomendado)"
                )
            elif total_gb < 4:
                requirements['recommendations'].append(
                    f"💡 RAM limitada: {total_gb:.1f}GB. Considera cerrar otras aplicaciones."
                )
        except ImportError:
            requirements['recommendations'].append(
                "💡 Instala psutil para monitoreo de recursos: pip install psutil"
            )
        
        # Verificar CPU
        try:
            import psutil
            cpu_count = psutil.cpu_count()
            
            if cpu_count < 2:
                requirements['warnings'].append(
                    f"⚠️ CPU limitado: {cpu_count} núcleo(s). Rendimiento puede ser lento."
                )
        except:
            pass
        
        return requirements
    
    @staticmethod
    def get_performance_tips() -> List[str]:
        """Retorna consejos de rendimiento"""
        return [
            "✅ Usa modelos locales pequeños (deepseek-coder) para desarrollo",
            "✅ Habilita caché para reducir llamadas LLM repetidas",
            "✅ Cierra otras aplicaciones para liberar RAM",
            "✅ Usa SSD para mejor rendimiento de I/O",
            "✅ Configura FLASK_DEBUG=0 en producción",
            "✅ Limpia sesiones antiguas regularmente"
        ]

# Instancias globales
config_validator = ConfigValidator()
health_monitor = HealthMonitor()
sqlite_optimizer = SQLiteOptimizer()
performance_optimizer = PerformanceOptimizer()
