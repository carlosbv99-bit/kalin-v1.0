"""
Sistema de logging estructurado para Kalin.
Proporciona logging con niveles, rotación de archivos y métricas.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional

class KalinLogger:
    """Logger centralizado para el sistema Kalin"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if KalinLogger._initialized:
            return
            
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.logger = logging.getLogger('kalin')
        self.logger.setLevel(logging.DEBUG)
        
        # Evitar duplicación de handlers
        if not self.logger.handlers:
            self._setup_handlers()
        
        KalinLogger._initialized = True
    
    def _setup_handlers(self):
        """Configura handlers para consola y archivos"""
        
        # Formato detallado para archivos
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Formato compacto para consola
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Handler de consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Handler de archivo principal (rotativo)
        main_log = os.path.join(self.log_dir, 'kalin.log')
        main_handler = RotatingFileHandler(
            main_log,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_handler.setLevel(logging.DEBUG)
        main_handler.setFormatter(file_formatter)
        self.logger.addHandler(main_handler)
        
        # Handler para errores críticos
        error_log = os.path.join(self.log_dir, 'kalin_errors.log')
        error_handler = RotatingFileHandler(
            error_log,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)
        
        # Handler específico para operaciones LLM
        llm_log = os.path.join(self.log_dir, 'kalin_llm.log')
        llm_handler = RotatingFileHandler(
            llm_log,
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        llm_handler.setLevel(logging.INFO)
        llm_handler.setFormatter(file_formatter)
        llm_logger = logging.getLogger('kalin.llm')
        llm_logger.addHandler(llm_handler)
        
        # Handler para operaciones de archivos
        file_ops_log = os.path.join(self.log_dir, 'kalin_file_ops.log')
        file_handler = RotatingFileHandler(
            file_ops_log,
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)
        file_logger = logging.getLogger('kalin.file_ops')
        file_logger.addHandler(file_handler)
    
    def get_logger(self, name: str = 'kalin') -> logging.Logger:
        """Obtiene un logger con el nombre especificado"""
        return logging.getLogger(name)
    
    def log_command(self, command: str, intention: str, params: dict = None):
        """Log específico para comandos ejecutados"""
        logger = self.get_logger('kalin.commands')
        extra_info = f" | params={params}" if params else ""
        logger.info(f"COMMAND: {command} | intention={intention}{extra_info}")
    
    def log_llm_call(self, provider: str, model: str, use_case: str, tokens_used: int = 0, cost: float = 0.0, success: bool = True):
        """Log específico para llamadas LLM"""
        logger = self.get_logger('kalin.llm')
        status = "SUCCESS" if success else "FAILED"
        logger.info(
            f"LLM_CALL: provider={provider} | model={model} | use_case={use_case} | "
            f"tokens={tokens_used} | cost=${cost:.4f} | status={status}"
        )
    
    def log_file_operation(self, operation: str, file_path: str, success: bool = True, error: str = None):
        """Log específico para operaciones de archivos"""
        logger = self.get_logger('kalin.file_ops')
        status = "SUCCESS" if success else "FAILED"
        error_info = f" | error={error}" if error else ""
        logger.info(f"FILE_OP: {operation} | path={file_path} | status={status}{error_info}")
    
    def log_performance(self, operation: str, duration: float, details: str = None):
        """Log de métricas de rendimiento"""
        logger = self.get_logger('kalin.performance')
        extra = f" | {details}" if details else ""
        logger.info(f"PERF: {operation} | duration={duration:.3f}s{extra}")


def get_logger(name: str = 'kalin') -> logging.Logger:
    """Función helper para obtener logger"""
    logger_instance = KalinLogger()
    return logger_instance.get_logger(name)


# Instancia global para acceso rápido
logger_instance = KalinLogger()
kalin_logger = logger_instance.get_logger('kalin')
