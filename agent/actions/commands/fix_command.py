"""
Comando Fix: Reparación automática de código.
"""

import os
from typing import Dict, Any
from flask import jsonify
from agent.actions.commands.base import BaseCommand
from agent.analyzer import analizar_codigo
from agent.actions.tools.fix_tool import generar_codigo, reparar_codigo
from agent.llm.client import is_available, get_provider_status
from agent.core.logger import get_logger

logger = get_logger('kalin.commands.fix')

class FixCommand(BaseCommand):
    """Comando para reparar archivos de código"""
    
    def validate(self, contexto: Dict[str, Any], utils: Dict[str, Any]) -> tuple:
        """Valida precondiciones para fix"""
        args = contexto.get("args", {})
        nombre = args.get("arg")
        ruta_proyecto = contexto.get("estado", {}).get("ruta_proyecto")
        
        if not nombre:
            return False, "❌ Usa: /fix archivo"
        
        if not ruta_proyecto:
            return False, "⚠️ Primero usa /setpath"
        
        if not is_available():
            status = get_provider_status()
            return False, " No hay proveedor LLM disponible. Revisa Ollama local o configura OPENAI_API_KEY/ANTHROPIC_API_KEY."
        
        return True, None
    
    def execute(self, contexto: Dict[str, Any], utils: Dict[str, Any]) -> Any:
        """Ejecuta la reparación de código"""
        from agent.core.state_manager import StateManager
        from agent.core.project_analyzer import ProjectAnalyzer
        
        args = contexto.get("args", {})
        nombre = args.get("arg")
        estado = contexto.get("estado", {})
        ruta_proyecto = estado.get("ruta_proyecto")
        
        state_manager = StateManager()
        if ruta_proyecto:
            state_manager.set_ruta(ruta_proyecto)
        
        # Buscar archivo
        project_analyzer = ProjectAnalyzer(ruta_proyecto)
        ruta_relativa = project_analyzer.buscar_archivo(nombre)
        
        if not ruta_relativa:
            ruta = utils["buscar_archivo_inteligente"](nombre, ruta_proyecto)
        else:
            ruta = os.path.join(ruta_proyecto, ruta_relativa)
        
        if not ruta:
            return jsonify({"respuesta": " Archivo no encontrado"})
        
        # Leer código
        codigo = utils["leer_archivo"](ruta)
        if not codigo:
            return jsonify({"respuesta": "❌ No se pudo leer el archivo"})
        
        logger.info(f"Fix command: analyzing {ruta}")
        
        # Registrar último archivo
        state_manager.set_ultimo_archivo(ruta, codigo)
        
        # Analizar y reparar
        analisis = analizar_codigo(codigo)
        logger.debug(f"Analysis result: {len(analisis)} chars")
        
        nuevo = reparar_codigo(codigo, analisis)
        
        if not nuevo:
            state_manager.registrar_fallo()
            status = get_provider_status()
            return jsonify({
                "respuesta": "❌ No se pudo generar código. Verifica el proveedor LLM configurado.",
                "status": status
            })
        
        # Procesar resultado
        nuevo_limpio = utils["limpiar_codigo"](nuevo) or nuevo
        valido = utils["es_codigo_valido"](nuevo_limpio)
        diff = utils["generar_diff"](codigo, nuevo_limpio)
        
        # Guardar estado
        state_manager.set_ultimo_fix(ruta, codigo, nuevo_limpio)
        
        logger.info(f"Fix completed: valid={valido}, diff_length={len(diff)}")
        
        return jsonify({
            "respuesta": "⚠️ Modo seguro activo (usa /apply para aplicar cambios)",
            "preview": nuevo_limpio[:800],
            "diff": diff,
            "valido": valido
        })
