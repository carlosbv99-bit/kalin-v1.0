"""
Plugin de ejemplo: Git Integration.
Proporciona comandos para operaciones de Git.
"""

import subprocess
from typing import List, Dict, Any
from flask import jsonify
from agent.core.plugin_manager import Plugin, PluginMetadata
from agent.actions.commands.base import BaseCommand
from agent.core.logger import get_logger
from agent.core.security_hardening import CommandSanitizer

logger = get_logger('kalin.plugins.git')

class GitStatusCommand(BaseCommand):
    """Comando para mostrar estado de Git"""
    
    def validate(self, contexto: Dict[str, Any], utils: Dict[str, Any]) -> tuple:
        ruta_proyecto = contexto.get("estado", {}).get("ruta_proyecto")
        
        if not ruta_proyecto:
            return False, "⚠️ Primero usa /setpath"
        
        return True, None
    
    def execute(self, contexto: Dict[str, Any], utils: Dict[str, Any]) -> Any:
        try:
            ruta_proyecto = contexto["estado"]["ruta_proyecto"]
            
            # Validar comando Git seguro
            is_safe, sanitized_cmd = CommandSanitizer.safe_run_git_command(
                'git status --short', 
                ruta_proyecto
            )
            
            if not is_safe:
                logger.warning(f"Git command blocked: {sanitized_cmd}")
                return jsonify({"respuesta": f"❌ Comando bloqueado por seguridad: {sanitized_cmd}"})
            
            # Ejecutar git status con shell=False (seguro)
            result = subprocess.run(
                ['git', 'status', '--short'],
                cwd=ruta_proyecto,
                capture_output=True,
                text=True,
                timeout=10,
                shell=False  # CRÍTICO: Nunca usar shell=True
            )
            
            if result.returncode != 0:
                return jsonify({"respuesta": "❌ No es un repositorio Git o Git no está instalado"})
            
            status = result.stdout.strip()
            
            if not status:
                return jsonify({"respuesta": "✅ Working tree limpio - sin cambios pendientes"})
            
            return jsonify({
                "respuesta": f"📊 Estado de Git:\n\n{status}"
            })
            
        except Exception as e:
            logger.error(f"Git status failed: {e}")
            return jsonify({"respuesta": f"❌ Error: {str(e)}"})

class GitCommitCommand(BaseCommand):
    """Comando para hacer commit"""
    
    def validate(self, contexto: Dict[str, Any], utils: Dict[str, Any]) -> tuple:
        ruta_proyecto = contexto.get("estado", {}).get("ruta_proyecto")
        mensaje = contexto.get("args", {}).get("arg")
        
        if not ruta_proyecto:
            return False, "⚠️ Primero usa /setpath"
        
        if not mensaje:
            return False, "❌ Usa: /commit \"mensaje del commit\""
        
        return True, None
    
    def execute(self, contexto: Dict[str, Any], utils: Dict[str, Any]) -> Any:
        try:
            ruta_proyecto = contexto["estado"]["ruta_proyecto"]
            mensaje = contexto["args"]["arg"]
            
            # Add all changes
            subprocess.run(['git', 'add', '.'], cwd=ruta_proyecto, timeout=10)
            
            # Commit
            result = subprocess.run(
                ['git', 'commit', '-m', mensaje],
                cwd=ruta_proyecto,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return jsonify({"respuesta": f"❌ Error en commit:\n{result.stderr}"})
            
            return jsonify({"respuesta": f"✅ Commit exitoso:\n{result.stdout}"})
            
        except Exception as e:
            logger.error(f"Git commit failed: {e}")
            return jsonify({"respuesta": f"❌ Error: {str(e)}"})

class GitPlugin(Plugin):
    """Plugin de integración con Git"""
    
    metadata = PluginMetadata(
        name="git-integration",
        version="1.0.0",
        description="Comandos para operaciones de Git (status, commit, etc.)",
        author="Kalin Team"
    )
    
    def on_load(self):
        logger.info("Git plugin loaded")
    
    def on_unload(self):
        logger.info("Git plugin unloaded")
    
    def get_commands(self) -> List[BaseCommand]:
        return [
            GitStatusCommand(),
            GitCommitCommand()
        ]
    
    def get_hooks(self) -> Dict[str, callable]:
        return {
            'on_file_change': self._on_file_change
        }
    
    def _on_file_change(self, file_path: str):
        """Hook que se llama cuando un archivo cambia"""
        logger.debug(f"File changed: {file_path}")
