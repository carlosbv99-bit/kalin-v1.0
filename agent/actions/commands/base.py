"""
Sistema de Command Pattern para Kalin.
Desacopla la lógica de ejecución del Executor principal.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from flask import jsonify
from agent.core.logger import get_logger

logger = get_logger('kalin.commands')

class BaseCommand(ABC):
    """Interfaz base para todos los comandos"""
    
    @abstractmethod
    def execute(self, contexto: Dict[str, Any], utils: Dict[str, Any]) -> Any:
        """Ejecuta el comando"""
        pass
    
    @abstractmethod
    def validate(self, contexto: Dict[str, Any], utils: Dict[str, Any]) -> tuple:
        """
        Valida precondiciones.
        Returns: (bool, Optional[str]) - (es_válido, mensaje_error)
        """
        pass

class CommandRegistry:
    """Registro central de comandos"""
    
    def __init__(self):
        self._commands: Dict[str, BaseCommand] = {}
    
    def register(self, name: str, command: BaseCommand):
        """Registra un comando"""
        self._commands[name] = command
        logger.info(f"Command registered: {name}")
    
    def get(self, name: str) -> Optional[BaseCommand]:
        """Obtiene un comando por nombre"""
        return self._commands.get(name)
    
    def list_commands(self) -> list:
        """Lista todos los comandos registrados"""
        return list(self._commands.keys())

# Instancia global del registry
command_registry = CommandRegistry()
