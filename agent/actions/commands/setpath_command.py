"""
Comando SetPath: Configuración de ruta del proyecto.
"""

from typing import Dict, Any
from flask import jsonify
from agent.actions.commands.base import BaseCommand
from agent.core.state_manager import StateManager
from agent.core.project_analyzer import ProjectAnalyzer
from agent.core.logger import get_logger

logger = get_logger('kalin.commands.setpath')

class SetPathCommand(BaseCommand):
    
    def validate(self, contexto: Dict[str, Any], utils: Dict[str, Any]) -> tuple:
        args = contexto.get("args", {})
        ruta = args.get("arg")
        
        if not ruta:
            return False, " No pude entender la ruta. Usa: /setpath E:\\carpeta"
        
        return True, None
    
    def execute(self, contexto: Dict[str, Any], utils: Dict[str, Any]) -> Any:
        args = contexto.get("args", {})
        ruta = args.get("arg")
        
        if ruta and len(ruta) <= 4:
            return jsonify({
                "respuesta": f"📂 ¿En qué carpeta del disco {ruta}? Por ejemplo:\n"
                            f"`/setpath {ruta}Proyecto`\n"
                            f"O dime: 'mi proyecto está en el disco E en la carpeta Proyecto'"
            })
        
        state_manager = StateManager()
        if not state_manager.set_ruta(ruta):
            return jsonify({"respuesta": f"❌ Ruta no válida: {ruta}"})
        
        # Inicializar project analyzer
        project_analyzer = ProjectAnalyzer(ruta)
        
        logger.info(f"Project path set: {ruta}")
        
        return jsonify({
            "respuesta": f"✅ Proyecto configurado en: {ruta}\n\nAhora puedes decir:\n• 'revisa mi proyecto'\n• 'analiza los archivos'\n• 'hay errores en el código'"
        })
