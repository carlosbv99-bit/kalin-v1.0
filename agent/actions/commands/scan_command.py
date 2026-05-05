"""
Comando Scan: Escaneo completo del proyecto.
"""

from typing import Dict, Any
from flask import jsonify
from agent.actions.commands.base import BaseCommand
from agent.core.project_analyzer import ProjectAnalyzer
from agent.core.logger import get_logger

logger = get_logger('kalin.commands.scan')

class ScanCommand(BaseCommand):
    
    def validate(self, contexto: Dict[str, Any], utils: Dict[str, Any]) -> tuple:
        ruta_proyecto = contexto.get("estado", {}).get("ruta_proyecto")
        
        if not ruta_proyecto:
            return False, "⚠️ Primero usa /setpath"
        
        return True, None
    
    def execute(self, contexto: Dict[str, Any], utils: Dict[str, Any]) -> Any:
        estado = contexto.get("estado", {})
        ruta_proyecto = estado.get("ruta_proyecto")
        
        project_analyzer = ProjectAnalyzer(ruta_proyecto)
        resumen = project_analyzer.get_resumen()
        
        logger.info(f"Project scan completed: {resumen['total_archivos']} files")
        
        return jsonify({
            "respuesta": "📊 Escaneo completado",
            "data": resumen
        })
