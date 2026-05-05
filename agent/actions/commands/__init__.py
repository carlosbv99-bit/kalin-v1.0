"""
Registro de comandos del sistema Kalin.
"""

from agent.actions.commands.base import command_registry
from agent.actions.commands.fix_command import FixCommand
from agent.actions.commands.setpath_command import SetPathCommand
from agent.actions.commands.scan_command import ScanCommand
from agent.actions.commands.chat_command import ChatCommand

# Registrar todos los comandos
command_registry.register("fix", FixCommand())
command_registry.register("setpath", SetPathCommand())
command_registry.register("scan", ScanCommand())
command_registry.register("chat", ChatCommand())
command_registry.register("greeting", ChatCommand())  # Greeting usa el mismo que chat

__all__ = ['command_registry']
