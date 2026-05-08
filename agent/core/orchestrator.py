from agent.core.brain import construir_contexto, planificar
from agent.actions.executor import Executor
from agent.core.logger import get_logger
from agent.core.conversation_manager import ConversationManager
from agent.core.conversation_memory import ConversationMemory as ConvMem
from agent.core.experience_memory import get_experience_memory
from agent.core.security import security_manager
from agent.core.prompt_security import prompt_detector, result_verifier, action_guardian
import time

logger = get_logger('kalin.orchestrator')

class Orchestrator:
    def __init__(self):
        self.executor = Executor()
        self.conversation_manager = None
        self.conversation_memory = None  # Nuevo sistema de memoria conversacional
        self.experience_memory = get_experience_memory()
        logger.info("Orchestrator initialized with ExperienceMemory and ConversationMemory")

    def handle(self, mensaje, estado, utils):
        """
        Maneja una petición del usuario con todos los componentes integrados.
        Incluye protección contra prompt injection y verificación de resultados.
        """
        start_time = time.time()
        
        # 0. PROTECCIÓN: Analizar prompt en busca de inyecciones
        prompt_analysis = prompt_detector.analyze_prompt(mensaje)
        
        if prompt_analysis['recommendation'] == 'block':
            logger.warning(f"Prompt blocked: {prompt_analysis['detected_patterns']}")
            return utils.get('jsonify')({
                "respuesta": "❌ Solicitud rechazada por motivos de seguridad. "
                           "Por favor, reformula tu pregunta sin intentar modificar las instrucciones del sistema."
            })
        
        if prompt_analysis['recommendation'] == 'warn':
            logger.warning(f"Suspicious prompt (risk={prompt_analysis['risk_level']}): {mensaje[:100]}")
            # Continuar pero con monitoreo adicional
        
        # Sanitizar prompt
        mensaje_sanitizado = prompt_detector.sanitize_prompt(mensaje)
        
        # 1. Inicializar conversation manager si no existe
        session_id = estado.get('session_id')
        if not self.conversation_manager:
            self.conversation_manager = ConversationManager(session_id=session_id)
            logger.info(f"ConversationManager created: {self.conversation_manager.session_id}")
        
        # 1.5 Inicializar conversation memory (sistema mejorado)
        if not self.conversation_memory:
            self.conversation_memory = ConvMem(
                session_id=session_id,
                max_history=20
            )
            logger.info(f"ConversationMemory initialized: {self.conversation_memory.session_id}")
        
        # 2. Registrar mensaje del usuario
        self.conversation_manager.add_message('user', mensaje_sanitizado)
        
        # 3. Validar seguridad del mensaje
        is_valid, security_error = security_manager.validate_code_content(mensaje_sanitizado)
        if not is_valid:
            logger.warning(f"Security violation: {security_error}")
            return utils.get('jsonify')({"respuesta": security_error})
        
        logger.info(f"Processing message: '{mensaje_sanitizado[:50]}...'")
        
        # 4. Construir contexto con conversación
        contexto = construir_contexto(mensaje_sanitizado, estado)
        contexto['conversation'] = self.conversation_manager
        contexto['conversation_memory'] = self.conversation_memory  # Agregar memoria conversacional
        contexto['security'] = security_manager
        
        # 5. Planificar
        contexto = planificar(contexto)
        
        # 6. Ejecutar con todos los componentes
        try:
            response = self.executor.ejecutar(contexto, utils)
            
            # 7. VERIFICACIÓN: Validar que el resultado sea completo
            if hasattr(response, 'get_json'):
                response_data = response.get_json()
                respuesta_texto = response_data.get('respuesta', '')
                
                # Verificar calidad del resultado
                intention = contexto.get('intencion', 'unknown')
                verification = result_verifier.verify_task_completion(intention, response_data)
                
                if not verification['completed'] and verification['errors']:
                    logger.warning(f"Task verification failed: {verification['errors']}")
                    # Agregar advertencia al usuario
                    if 'respuesta' in response_data:
                        response_data['respuesta'] += "\n\n⚠️ Nota: La tarea puede estar incompleta. Verifica el resultado."
                
                self.conversation_manager.add_message('assistant', respuesta_texto)
            
            # 8. Guardar sesión
            self.conversation_manager.save()
            
            # 9. Log de rendimiento
            duration = time.time() - start_time
            logger.info(f"Request completed in {duration:.3f}s")
            
            from agent.core.logger import logger_instance
            logger_instance.log_performance(
                'request_handle',
                duration,
                f"intention={contexto['intencion']}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            self.conversation_manager.add_message('assistant', f"❌ Error: {str(e)}")
            self.conversation_manager.save()
            
            return utils.get('jsonify')({"respuesta": f"❌ Error interno: {str(e)}"})