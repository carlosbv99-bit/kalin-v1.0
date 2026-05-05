"""
Comando Chat: Conversación general con IA contextual.
"""

from typing import Dict, Any
from flask import jsonify
from agent.actions.commands.base import BaseCommand
from agent.llm.client import generate, is_available
from agent.core.logger import get_logger

logger = get_logger('kalin.commands.chat')

class ChatCommand(BaseCommand):
    
    def validate(self, contexto: Dict[str, Any], utils: Dict[str, Any]) -> tuple:
        if not is_available():
            return False, "⚠️ No hay IA disponible. Asegúrate de que Ollama esté corriendo con: ollama serve"
        return True, None
    
    def execute(self, contexto: Dict[str, Any], utils: Dict[str, Any]) -> Any:
        mensaje_usuario = contexto.get("mensaje", "")
        
        prompt_sistema = """Eres Kalin, un asistente de IA experto en desarrollo de software.
- Eres amigable, útil y conversacional
- Responde en el mismo idioma del usuario
- Puedes ayudar con código, proyectos, debugging, etc.
- Si el usuario no ha configurado un proyecto, sugiere que use /setpath <ruta>
- Sé conciso pero completo"""
        
        prompt_completo = f"""{prompt_sistema}

Usuario: {mensaje_usuario}

Respuesta:"""
        
        try:
            respuesta_ia = generate(prompt_completo)
            if not respuesta_ia or len(respuesta_ia.strip()) < 10:
                respuesta_ia = f"👋 ¡Hola! Soy Kalin. {mensaje_usuario}"
            
            logger.info(f"Chat response generated: {len(respuesta_ia)} chars")
            
            return jsonify({"respuesta": respuesta_ia})
        except Exception as e:
            logger.error(f"Chat command failed: {e}")
            return jsonify({"respuesta": f"❌ Error al procesar: {str(e)}"})
