"""
Capa de Orquestación - Gestiona el flujo completo de procesamiento
Separa: Recepción → Planificación → Ejecución → Validación → Respuesta
Permite escalabilidad a múltiples agentes en el futuro
"""

import time
from typing import Dict, Any, Optional, List
from agent.core.logger import get_logger

logger = get_logger('kalin.orchestrator_layer')


class OrchestrationLayer:
    """
    Capa de orquestación que coordina el flujo de trabajo.
    
    Responsabilidades:
    1. Recepción y validación de entrada
    2. Análisis de intención y contexto
    3. Planificación de tareas
    4. Coordinación de ejecución (actualmente 1 agente, preparado para N)
    5. Validación de resultados
    6. Formateo de respuesta
    """
    
    def __init__(self):
        self.agent_registry = {}  # Registro de agentes disponibles
        self.execution_stats = {
            'total_requests': 0,
            'avg_response_time': 0,
            'errors': 0
        }
        # Sistema de bloqueo de lenguaje por sesión
        self.session_language_lock = {}  # {session_id: language}
        
        # Inicializar Patch Manager
        from agent.core.patch_manager import get_patch_manager
        self.patch_manager = get_patch_manager()
        
        logger.info("OrchestrationLayer initialized with PatchManager")
    
    def register_agent(self, agent_name: str, agent_instance):
        """Registra un agente en el sistema"""
        self.agent_registry[agent_name] = agent_instance
        logger.info(f"Agent registered: {agent_name}")
    
    def process_request(
        self,
        user_input: str,
        context: Dict[str, Any],
        utils: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Procesa una solicitud completa a través del pipeline de orquestación.
        
        Args:
            user_input: Mensaje del usuario
            context: Contexto de la sesión (ruta proyecto, historial, etc.)
            utils: Utilidades disponibles (leer_archivo, escribir_archivo, etc.)
        
        Returns:
            Diccionario con la respuesta procesada
        """
        start_time = time.time()
        self.execution_stats['total_requests'] += 1
        
        # Crear identidad de tarea
        from agent.core.task_identity import get_task_manager
        task_mgr = get_task_manager()
        session_id = context.get('session_id', 'default')
        
        task_id = task_mgr.create_task(
            session_id=session_id,
            agent_id='orchestration_layer',
            context={'user_input_length': len(user_input)}
        )
        
        try:
            # Iniciar tarea
            task_mgr.start_task(task_id)
            
            # FAST-PATH: Detectar requests simples (chat básico, preguntas cortas)
            if self._is_simple_request(user_input):
                return self._handle_simple_request(
                    user_input, session_id, task_id, start_time, task_mgr
                )
            
            # FASE 0: Almacenar mensaje en MemoryManager
            session_id = context.get('session_id', 'default')
            from agent.core.memory_manager import get_memory_manager
            memory_mgr = get_memory_manager()
            
            # Emitir evento de inicio de request
            from agent.core.event_bus import get_event_bus, EVENT_LLM_REQUEST
            event_bus = get_event_bus()
            event_bus.emit(EVENT_LLM_REQUEST, {
                'session_id': session_id,
                'user_input_length': len(user_input),
                'intention': 'pending'
            }, source='orchestration_layer')
            
            # Almacenar mensaje del usuario
            memory_mgr.store(
                session_id=session_id,
                message=user_input,
                role='user',
                metadata={'timestamp': start_time}
            )
            
            # FASE 0.5: Actualizar ContextManager modular
            from agent.core.context_manager import get_context_manager
            context_mgr = get_context_manager()
            
            # Actualizar contexto conversacional
            context_mgr.update_conversation('user', user_input)
            
            # Actualizar contexto de proyecto si hay ruta
            if context.get('ruta_proyecto'):
                context_mgr.update_project(context['ruta_proyecto'])
                
                # Sincronizar con ProjectState
                from agent.core.project_state import get_project_state_manager
                state_mgr = get_project_state_manager()
                project_state = state_mgr.set_active_project(context['ruta_proyecto'])
            
            # FASE 1: Recepción y Validación
            validated_input = self._validate_input(user_input)
            
            # FASE 2: Análisis de Intención
            intention = self._analyze_intention(validated_input, context)
            
            # FASE 3: Planificación
            plan = self._create_plan(intention, validated_input, context)
            
            # APLICAR BLOQUEO DE LENGUAJE ANTES DE EJECUTAR
            session_id = context.get('session_id', 'default')
            existing_code = context.get('current_code', '') or context.get('codigo_actual', '')
            
            if existing_code and len(existing_code.strip()) > 10:
                # Detectar lenguaje del código existente
                detected_lang = self._detect_language(existing_code)
                
                # Si no hay bloqueo establecido, crearlo INMEDIATAMENTE
                if session_id not in self.session_language_lock and detected_lang != 'unknown':
                    self.session_language_lock[session_id] = detected_lang
                    logger.info(f"🔒 Lenguaje bloqueado para sesión {session_id[:8]}: {detected_lang.upper()}")
                
                # Si hay bloqueo, VALIDAR que el nuevo fragmento sea del mismo lenguaje
                if session_id in self.session_language_lock:
                    locked_lang = self.session_language_lock[session_id]
                    
                    # Detectar lenguaje del NUEVO fragmento generado por LLM
                    new_fragment_check = str(final_result).strip()
                    new_detected_lang = self._detect_language(new_fragment_check)
                    
                    # VALIDACIÓN CRÍTICA: Si el LLM generó código en lenguaje diferente, RECHAZAR
                    if new_detected_lang != 'unknown' and new_detected_lang != locked_lang:
                        logger.warning(f"⚠️ BLOQUEO ACTIVADO: LLM intentó cambiar de {locked_lang.upper()} a {new_detected_lang.upper()}. Rechazando...")
                        
                        # Mantener código original y advertir al usuario
                        final_result = existing_code
                        respuesta_text = validated_result.get('respuesta', '')
                        validated_result['respuesta'] = f"{respuesta_text}\n\n⚠️ ERROR DETECTADO: El sistema intentó cambiar el lenguaje de {locked_lang.upper()} a {new_detected_lang.upper()}, pero esto está PROHIBIDO. Se mantuvo el código {locked_lang.upper()} original.\n\nPor favor, reformula tu petición especificando que quieres AGREGAR/MODIFICAR en {locked_lang.upper()}."
                        
                        # Retornar inmediatamente sin aplicar cambios
                        return {
                            'respuesta': validated_result['respuesta'],
                            'tool_results': results,
                            'intention': intention,
                            'language_lock_violation': True,
                            'locked_language': locked_lang
                        }
                    
                    # Modificar el prompt en el plan si es intención 'create'
                    if intention == 'create' and plan.get('steps'):
                        for step in plan['steps']:
                            if 'generate' in str(step.get('action', '')):
                                # Agregar instrucción MUY EXPLÍCITA de lenguaje bloqueado al prompt original
                                original_prompt = step.get('prompt', '')
                                if original_prompt:
                                    step['prompt'] = f"""{original_prompt}

🔒🔒🔒 CRÍTICO - LENGUAJE BLOQUEADO: {locked_lang.upper()} 🔒🔒🔒
- El código actual ES {locked_lang.upper()}
- DEBES usar SOLO {locked_lang.upper()}
- PROHIBIDO cambiar a Python, JavaScript u otro lenguaje
- NO regeneres el archivo completo
- AGREGA o MODIFICA el código existente en {locked_lang.upper()}
- Responde ÚNICAMENTE con código {locked_lang.upper()} válido"""
                                    logger.info(f"🔒 Prompt reforzado con lenguaje bloqueado: {locked_lang.upper()}")
            
            # FASE 4: Ejecución (coordina agentes)
            result = self._execute_plan(plan, context, utils, context_mgr)
            
            # FASE 5: Validación de Resultado
            validated_result = self._validate_result(result, intention)
            
            # FASE 6: Formateo de Respuesta
            response = self._format_response(validated_result, intention)
            
            # Almacenar respuesta del asistente en MemoryManager
            memory_mgr.store(
                session_id=session_id,
                message=response.get('respuesta', ''),
                role='assistant',
                metadata={
                    'intention': intention,
                    'duration': time.time() - start_time,
                    'validated': validated_result.get('validated', False)
                }
            )
            
            # Actualizar contexto conversacional con respuesta
            if context_mgr:
                context_mgr.update_conversation('assistant', response.get('respuesta', ''))
            
            # Agregar task_id a la respuesta
            response['task_id'] = task_id
            response['session_id'] = session_id
            
            # Actualizar estadísticas
            duration = time.time() - start_time
            self._update_stats(duration, success=True)
            
            # Completar tarea exitosamente
            task_mgr.complete_task(task_id, duration)
            
            # Emitir evento de respuesta LLM
            from agent.core.event_bus import EVENT_LLM_RESPONSE
            event_bus.emit(EVENT_LLM_RESPONSE, {
                'task_id': task_id,
                'session_id': session_id,
                'intention': intention,
                'duration': duration,
                'response_length': len(response.get('respuesta', ''))
            }, source='orchestration_layer')
            
            logger.info(f"Request processed successfully in {duration:.3f}s - {task_id[:8]}")
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            self._update_stats(duration, success=False)
            
            # Marcar tarea como fallida
            task_mgr.fail_task(task_id, str(e), duration)
            
            logger.error(f"Request failed after {duration:.3f}s: {e} - {task_id[:8]}")
            return self._format_error_response(e)
    
    def _validate_input(self, user_input: str) -> str:
        """Valida y sanitiza la entrada del usuario"""
        if not user_input or not user_input.strip():
            raise ValueError("Input vacío")
        
        # Sanitización básica
        sanitized = user_input.strip()
        
        # Verificar longitud máxima (previene ataques)
        if len(sanitized) > 10000:
            raise ValueError("Input demasiado largo (máx 10000 chars)")
        
        return sanitized
    
    def _analyze_intention(self, user_input: str, context: Dict) -> str:
        """
        Analiza la intención del usuario.
        
        Retorna una categoría de intención:
        - 'chat': Conversación general (saludos, preguntas, charla)
        - 'create': Crear/modificar código
        - 'fix': Corregir errores
        - 'enhance': Mejorar código existente
        - 'analyze': Analizar código
        - 'refactor': Refactorizar código
        """
        user_input_lower = user_input.lower().strip()
        
        # ===== PRIORIDAD 1: Detectar CHAT conversacional =====
        chat_patterns = [
            # Saludos
            r'\b(hola|hey|buenas|hi|hello|que tal|como estas)\b',
            # Despedidas
            r'\b(adios|bye|hasta luego|nos vemos|chao)\b',
            # Agradecimientos
            r'\b(gracias|thanks|genial|perfecto|excelente)\b',
            # Preguntas generales sobre el asistente
            r'\b(quien eres|que puedes|que haces|tu nombre)\b',
            # Estado emocional/social
            r'\b(como estas|como vas|todo bien)\b',
            # Conversación casual sin intención técnica
            r'\b(jaja|jajaja|ok|vale|si|no|claro|entendido)\b',
            # Declaraciones de contexto sin acción específica
            r'\b(trabajaremos|hoy vamos|vamos a|empezamos)\b.*\b(html|python|codigo|programar)\b',
        ]
        
        import re
        for pattern in chat_patterns:
            if re.search(pattern, user_input_lower):
                # Verificar que NO haya palabras técnicas en el mensaje
                tech_words = ['crear', 'generar', 'codigo', 'html', 'python', 'agrega', 'modifica', 'funcion', 'clase']
                if not any(word in user_input_lower for word in tech_words):
                    logger.debug(f"Intention detected: chat (conversational)")
                    return 'chat'
        
        # ===== PRIORIDAD 2: Detectar intenciones de código =====
        intention_keywords = {
            'create': ['crear', 'generar', 'nuevo', 'hacer', 'construir', 'agrega', 'añade', 'pon', 'inserta', 'dibuja', 'crea'],
            'fix': ['corregir', 'arreglar', 'fix', 'reparar', 'error', 'bug', 'problema'],
            'enhance': ['mejorar', 'optimizar', 'enhance', 'upgrade', 'actualizar'],
            'analyze': ['analizar', 'revisar', 'explicar', 'entender', 'que hace'],
            'refactor': ['refactorizar', 'refactor', 'limpiar', 'organizar', 'ordenar'],
        }
        
        # Detectar intención por palabras clave
        for intention, keywords in intention_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                logger.debug(f"Intention detected: {intention} (code-related)")
                return intention
        
        # Default: Si hay código en el contexto, asumir que quiere modificarlo/agregar
        existing_code = context.get('current_code', '') or context.get('codigo_actual', '')
        if existing_code and len(existing_code.strip()) > 10:
            # Verificar si el mensaje parece una continuación/instrucción breve
            short_phrases = ['un circulo', 'un cuadrado', 'un boton', 'una linea', 'un triangulo', 'abajo', 'arriba', 'derecha', 'izquierda', 'debajo', 'al lado']
            if any(phrase in user_input_lower for phrase in short_phrases) or len(user_input.split()) <= 4:
                logger.debug(f"Intention detected: create (short instruction with existing code)")
                return 'create'
            logger.debug(f"Intention detected: create (modification of existing code)")
            return 'create'
        
        # Si no hay código y no es claramente chat, preguntar o tratar como chat
        logger.debug(f"Intention detected: chat (default)")
        return 'chat'
    
    def _create_plan(
        self,
        intention: str,
        user_input: str,
        context: Dict
    ) -> Dict[str, Any]:
        """
        Crea un plan de ejecución basado en la intención.
        
        El plan define:
        - Qué agente(s) usar
        - En qué orden ejecutar
        - Parámetros específicos
        """
        plan = {
            'intention': intention,
            'steps': [],
            'agents_required': [],
            'parameters': {
                'user_input': user_input,
                'context': context
            }
        }
        
        # Definir pasos según intención
        if intention == 'create':
            plan['steps'] = [
                {'action': 'generate_code', 'description': 'Generar código desde cero'},
                {'action': 'validate_syntax', 'description': 'Validar sintaxis'},
                {'action': 'save_file', 'description': 'Guardar archivo'}
            ]
            plan['agents_required'] = ['code_generator']
            
        elif intention == 'fix':
            plan['steps'] = [
                {'action': 'analyze_error', 'description': 'Analizar error'},
                {'action': 'generate_fix', 'description': 'Generar corrección'},
                {'action': 'apply_fix', 'description': 'Aplicar corrección'},
                {'action': 'verify_fix', 'description': 'Verificar corrección'}
            ]
            plan['agents_required'] = ['code_analyzer', 'code_generator']
            
        elif intention == 'analyze':
            plan['steps'] = [
                {'action': 'read_code', 'description': 'Leer código'},
                {'action': 'analyze_structure', 'description': 'Analizar estructura'},
                {'action': 'generate_report', 'description': 'Generar reporte'}
            ]
            plan['agents_required'] = ['code_analyzer']
            
        else:  # chat, enhance, refactor
            plan['steps'] = [
                {'action': 'process_request', 'description': 'Procesar solicitud'}
            ]
            plan['agents_required'] = ['general_assistant']
        
        logger.debug(f"Plan created: {len(plan['steps'])} steps")
        return plan
    
    def _execute_plan(
        self,
        plan: Dict[str, Any],
        context: Dict[str, Any],
        utils: Dict[str, Any],
        context_mgr = None
    ) -> Dict[str, Any]:
        """
        Ejecuta el plan usando ToolManager desacoplado.
        
        Los agentes (frontend, backend, QA) usan las mismas tools
        a través del ToolManager centralizado.
        """
        from agent.core.tool_manager import get_tool_manager
        
        tool_manager = get_tool_manager()
        intention = plan['intention']
        user_input = plan['parameters']['user_input']
        
        # DETECTAR SI HAY CÓDIGO EXISTENTE Y FORZAR LENGUAJE EN MODIFICACIONES
        existing_code = context.get('current_code', '') or context.get('codigo_actual', '')
        if existing_code and len(existing_code.strip()) > 10:
            import re
            lang_detected = 'unknown'
            
            # HTML/SVG (prioridad ALTA - verificar etiquetas específicas)
            html_tags = ['<html', '<div', '<span', '<svg', '<circle', '<rect', '<body', '<head', '<p>', '<button', '<input', '<img', '<h1', '<h2', '<h3', '<ul', '<li', '<table', '<canvas']
            if any(tag in existing_code.lower() for tag in html_tags):
                lang_detected = 'html'
            # Python
            elif any(kw in existing_code for kw in ['def ', 'import ', 'print(', 'class ']):
                lang_detected = 'python'
            # C/C++
            elif '#include' in existing_code:
                lang_detected = 'c'
            # Java
            elif 'public class' in existing_code or 'System.out' in existing_code:
                lang_detected = 'java'
            # JavaScript
            elif any(kw in existing_code for kw in ['function', 'const ', 'let ', 'var ', 'console.log']):
                lang_detected = 'javascript'
            
            # Si detectamos un lenguaje, bloquearlo para esta sesión
            session_id = context.get('session_id', 'default')
            if lang_detected != 'unknown':
                # Bloquear lenguaje si no está ya bloqueado
                if session_id not in self.session_language_lock:
                    self.session_language_lock[session_id] = lang_detected
                    logger.info(f"🔒 BLOQUEO AUTOMÁTICO: Lenguaje {lang_detected.upper()} bloqueado para sesión {session_id[:8]}")
                else:
                    # Usar lenguaje bloqueado existente
                    lang_detected = self.session_language_lock[session_id]
                    logger.info(f"🔒 Usando lenguaje bloqueado: {lang_detected.upper()}")
                
                # Agregar instrucción MUY FUERTE al prompt
                user_input = f"{user_input}\n\n🔒🔒🔒 CRÍTICO - LENGUAJE OBLIGATORIO: {lang_detected.upper()} 🔒🔒🔒\n- El código actual ES {lang_detected.upper()}\n- DEBES usar SOLO {lang_detected.upper()}\n- PROHIBIDO usar Python, matplotlib u otro lenguaje\n- AGREGA al código existente, NO lo reemplaces\n- Responde ÚNICAMENTE con código {lang_detected.upper()} válido\n- Si generas otro lenguaje, el sistema RECHAZARÁ tu respuesta"
        
        # Mapear intención a tool calls
        tool_calls = []
        
        if intention == 'create':
            # Verificar si hay código existente (modificación vs creación nueva)
            existing_code = context.get('current_code', '') or context.get('codigo_actual', '')
            
            if existing_code and len(existing_code.strip()) > 10:
                # MODIFICACIÓN con sistema de PARCHES - generar SOLO el cambio
                
                # Verificar si hay lenguaje bloqueado para esta sesión
                session_id = context.get('session_id', 'default')
                locked_lang = self.session_language_lock.get(session_id, None)
                
                lang_instruction = ""
                if locked_lang:
                    lang_instruction = f"""
⚠️ CRÍTICO - LENGUAJE BLOQUEADO: {locked_lang.upper()}
- El código actual ES {locked_lang.upper()}
- DEBES usar SOLO {locked_lang.upper()}
- PROHIBIDO cambiar a otro lenguaje
- Responde ÚNICAMENTE con código {locked_lang.upper()} válido"""
                
                # Obtener contexto conversacional (historial reciente)
                from agent.core.memory_manager import get_memory_manager
                memory_mgr = get_memory_manager()
                conversation_context = memory_mgr.get_context(session_id, window=3)  # Últimos 3 intercambios
                
                context_instruction = ""
                if conversation_context:
                    context_instruction = f"""

📝 CONTEXTO CONVERSACIONAL RECIENTE:
{conversation_context}

IMPORTANTE: Considera este contexto para mantener coherencia en tu respuesta."""
                
                prompt = f"""Tienes este código actual:
{existing_code}

TAREA DEL USUARIO: {user_input}{lang_instruction}{context_instruction}

INSTRUCCIONES CRÍTICAS:
1. Genera ÚNICAMENTE el NUEVO elemento/código que pide el usuario
2. NO regeneres el archivo completo
3. NO incluyas código existente en tu respuesta
4. Responde SOLO con el fragmento nuevo (ej: <div>...</div> o def funcion(): ...)
5. El sistema aplicará automáticamente tu cambio como un parche
6. AGREGA al código existente, NO lo reemplaces completamente

Ejemplos correctos:
- Usuario: "agrega un círculo rojo"
  Tu respuesta: <circle cx="100" cy="100" r="50" fill="red"></circle>

- Usuario: "agrega una función sumar"
  Tu respuesta: def sumar(a, b):\n    return a + b

IMPORTANTE: Genera SOLO el nuevo fragmento, nada más."""
            else:
                # Creación desde cero
                prompt = f"Genera código para: {user_input}"
            
            tool_calls = [
                {'tool': 'generate_with_llm', 'params': {
                    'prompt': prompt,
                    'temperature': 0.8
                }}
                # NOTA: Eliminamos write_file porque el código generado se devuelve directamente
                # El frontend es responsable de mostrar/guardar el código según sea necesario
            ]
        elif intention == 'fix':
            tool_calls = [
                {'tool': 'read_file', 'params': {'path': context.get('ruta_proyecto', '') + '/main.py'}},
                {'tool': 'analyze_code', 'params': {'code': 'PLACEHOLDER'}},
                {'tool': 'generate_with_llm', 'params': {
                    'prompt': f"Corrige errores en: {user_input}",
                    'temperature': 0.2
                }}
            ]
        elif intention == 'analyze':
            tool_calls = [
                {'tool': 'read_file', 'params': {'path': context.get('ruta_proyecto', '') + '/main.py'}},
                {'tool': 'analyze_code', 'params': {'code': 'PLACEHOLDER'}}
            ]
        else:  # chat - AGENTE CONVERSACIONAL
            # Prompt para comportamiento de chatbot amigable pero directo
            tool_calls = [
                {'tool': 'generate_with_llm', 'params': {
                    'prompt': f"""Eres Kalin, un asistente de programación amigable y eficiente.

Mensaje del usuario: {user_input}

INSTRUCCIONES IMPORTANTES:
1. Si el usuario pide crear/generar/modificar código → responde SOLO con el código, sin explicaciones largas
2. Si es una pregunta general sobre programación → responde brevemente y ofrece ayuda práctica
3. Si es un saludo o conversación casual → sé amable pero BREVE (máximo 1-2 frases)
4. NUNCA preguntes "¿en qué lenguaje?" si el usuario ya lo mencionó
5. NUNCA digas "¿quieres que te muestre cómo?" → simplemente HAZLO
6. Sé DIRECTO y PRÁCTICO

Ejemplos de respuestas correctas:
- Usuario: "hola" → Tú: "¡Hola! ¿En qué puedo ayudarte?"
- Usuario: "crea un botón en HTML" → Tú: [código HTML del botón]
- Usuario: "qué eres" → Tú: "Soy Kalin, tu asistente de programación. Puedo generar código en HTML, CSS, Python, JavaScript y más."

Responde en español. Sé CONCISO.""",
                    'temperature': 0.7  # Balance entre creatividad y precisión
                }}
            ]
        
        # Ejecutar tools secuencialmente
        results = []
        last_result = None
        
        # Iniciar contexto de ejecución si hay context_mgr
        if context_mgr:
            context_mgr.start_execution(len(tool_calls))
        
        for call in tool_calls:
            # Reemplazar PLACEHOLDER con resultado anterior si existe
            if 'params' in call and last_result is not None:
                for key, value in call['params'].items():
                    if value == 'PLACEHOLDER':
                        call['params'][key] = last_result
            
            try:
                result = tool_manager.run(call['tool'], call['params'], context)
                results.append({'tool': call['tool'], 'success': True, 'result': result})
                last_result = result
                
                # Registrar en contexto de ejecución
                if context_mgr:
                    context_mgr.record_tool_result(
                        tool=call['tool'],
                        params=call['params'],
                        result=result,
                        success=True
                    )
            except Exception as e:
                results.append({'tool': call['tool'], 'success': False, 'error': str(e)})
                logger.error(f"Tool execution failed: {e}")
                
                # Registrar error en contexto
                if context_mgr:
                    context_mgr.execution.record_error(str(e))
                
                break
        
        # Retornar último resultado exitoso
        successful_results = [r for r in results if r['success']]
        if successful_results:
            final_result = successful_results[-1]['result']
            
            # Si hay código existente y la intención es 'create', aplicar como PARCH
            existing_code = context.get('current_code', '') or context.get('codigo_actual', '')
            if intention == 'create' and existing_code and len(existing_code.strip()) > 10:
                new_fragment = str(final_result).strip()
                
                # Detectar lenguaje del código existente
                is_html = any(tag in existing_code.lower() for tag in ['<html', '<div', '<span', '<svg', '<circle', '<rect', '<body'])
                is_python = any(kw in existing_code.lower() for kw in ['import ', 'def ', 'print(', 'class '])
                is_javascript = any(kw in existing_code.lower() for kw in ['function', 'const ', 'let ', 'var ', 'document.', 'console.log'])
                
                # Detectar lenguaje del nuevo fragmento
                new_is_python = any(kw in new_fragment.lower() for kw in ['import ', 'def ', 'print(', 'matplotlib'])
                new_is_javascript = any(kw in new_fragment.lower() for kw in ['function', 'const ', 'let ', 'var ', 'document.', 'console.log'])
                
                # VALIDACIÓN: Detectar cambio de lenguaje no deseado
                language_mismatch = False
                if is_html and (new_is_python or new_is_javascript):
                    language_mismatch = True
                    logger.warning(f"⚠️ LLM cambió de HTML a {'Python' if new_is_python else 'JavaScript'}. Rechazando...")
                
                if language_mismatch:
                    # Rechazar el código incorrecto y mantener el original
                    final_result = existing_code
                    respuesta_text = validated_result.get('respuesta', '')
                    validated_result['respuesta'] = respuesta_text + f"\n\n⚠️ Mantuve el código anterior. El LLM intentó cambiar a {'Python' if new_is_python else 'JavaScript'}, pero conservé {'HTML' if is_html else 'código'} según el contexto."
                else:
                    # Aplicar parche usando PatchManager
                    from agent.core.patch_manager import Patch, PatchOperation, PatchLocation
                    
                    # Crear snapshot antes de modificar
                    session_id = context.get('session_id', 'default')
                    self.patch_manager.create_snapshot(
                        project_id=session_id,
                        files={'current_file': existing_code},
                        user_request=user_input
                    )
                    
                    # Determinar ubicación del parche según lenguaje
                    if is_html:
                        # Para HTML, insertar antes de </body>
                        location = PatchLocation(
                            anchor_pattern=r'</body>|</html>',
                            position='before'
                        )
                        
                        # Crear parche
                        patch = Patch(
                            file_path='current_file',
                            operation=PatchOperation.INSERT,
                            content=new_fragment,
                            location=location,
                            description=f"Modificación solicitada: {user_input}"
                        )
                        
                        # Aplicar parche
                        patched_content, patch_metadata = self.patch_manager.apply_patch(
                            existing_code,
                            patch,
                            validate=True
                        )
                        
                        if patch_metadata['success'] and patch_metadata['changes_made']:
                            final_result = patched_content
                            logger.info(f"✅ Parche aplicado exitosamente: {patch_metadata['lines_affected']} líneas afectadas")
                            
                            # Registrar parche en historial
                            self.patch_manager.record_patch(session_id, patch)
                        else:
                            # Si falla el parche, usar fallback de combinación simple
                            logger.warning(f"⚠️ Parche falló ({patch_metadata['error']}), usando fallback")
                            final_result = existing_code + '\n\n' + new_fragment
                    
                    elif is_python or is_javascript:
                        # Para Python/JavaScript, SIEMPRE agregar al código existente
                        # MEJORA: Preservar todo el código anterior y agregar lo nuevo
                        
                        # Verificar si el nuevo fragmento ya está incluido (evitar duplicados)
                        if new_fragment.strip() in existing_code:
                            final_result = existing_code
                            logger.info("✅ Fragmento ya existe en código, manteniendo original")
                        else:
                            # Detectar estructura del código para inserción inteligente
                            existing_lines = existing_code.split('\n')
                            new_lines = new_fragment.split('\n')
                            
                            # Estrategia 1: Si hay solapamiento significativo, mantener solo el nuevo
                            existing_set = set(line.strip() for line in existing_lines if line.strip())
                            new_set = set(line.strip() for line in new_lines if line.strip())
                            overlap = len(existing_set.intersection(new_set)) / max(len(new_set), 1)
                            
                            if overlap > 0.8:
                                # El LLM regeneró todo el archivo - usar solo el nuevo
                                final_result = new_fragment
                                logger.info(f"Código completo regenerado por LLM (overlap: {overlap:.2f})")
                            else:
                                # AGREGAR al código existente (comportamiento normal)
                                # Insertar después del último bloque de código relevante
                                final_result = self._smart_append_code(existing_code, new_fragment, is_python)
                                logger.info(f"✅ Código agregado exitosamente (overlap: {overlap:.2f})")
            
            return {
                'respuesta': final_result if isinstance(final_result, str) else str(final_result),
                'tool_results': results,
                'intention': intention
            }
        else:
            return {
                'respuesta': '❌ No se pudo completar la solicitud',
                'tool_results': results,
                'intention': intention
            }
    
    def _validate_result(
        self,
        result: Any,
        intention: str
    ) -> Dict[str, Any]:
        """
        Valida que el resultado sea correcto y completo.
        """
        # Si el resultado ya es un dict con 'respuesta', retornarlo
        if isinstance(result, dict) and 'respuesta' in result:
            return result
        
        # Si es otro tipo, envolverlo
        return {
            'respuesta': str(result) if result else 'Sin respuesta',
            'intention': intention,
            'validated': True
        }
    
    def _format_response(
        self,
        validated_result: Dict[str, Any],
        intention: str
    ) -> Dict[str, Any]:
        """
        Formatea la respuesta final para el usuario.
        Extrae código si existe y lo coloca en campo 'code' para el frontend.
        """
        respuesta_text = validated_result.get('respuesta', '')
        
        # Intentar extraer código de la respuesta
        extracted_code = self._extract_code_from_response(respuesta_text)
        
        response = {
            'respuesta': respuesta_text,
            'intention': intention,
            'metadata': {
                'validated': validated_result.get('validated', False),
                'timestamp': time.time()
            }
        }
        
        # Si se extrajo código, agregarlo en campo separado
        if extracted_code:
            response['code'] = extracted_code
            logger.debug(f"Code extracted: {len(extracted_code)} chars")
        
        return response
    
    def _format_error_response(self, error: Exception) -> Dict[str, Any]:
        """Formatea una respuesta de error"""
        return {
            'respuesta': f"❌ Error: {str(error)}",
            'error': True,
            'error_type': type(error).__name__
        }
    
    def _detect_language(self, code: str) -> str:
        """Detecta el lenguaje del código - VERSIÓN MEJORADA"""
        if not code or len(code.strip()) < 5:
            return 'unknown'
        
        code_lower = code.lower()
        
        # HTML - DETECCIÓN MEJORADA (prioridad alta)
        html_indicators = [
            '<html', '<div', '<span', '<svg', '<circle', '<rect', '<body',
            '<head', '<title', '<h1', '<h2', '<p', '<button', '<input',
            '<form', '<table', '<ul', '<ol', '<li', '<a ', '<img',
            '<video', '<audio', '<canvas', '<script', '<style',
            '<!doctype', '<meta', '<link'
        ]
        html_count = sum(1 for tag in html_indicators if tag in code_lower)
        if html_count >= 1:
            return 'html'
        
        # Python
        python_indicators = ['def ', 'import ', 'print(', 'class ', 'from ', 'elif ', 'except:', 'finally:']
        python_count = sum(1 for kw in python_indicators if kw in code)
        if python_count >= 1:
            return 'python'
        
        # JavaScript
        js_indicators = ['function', 'const ', 'let ', 'var ', 'console.log', 'document.', 'window.', '=>', 'addEventListener']
        js_count = sum(1 for kw in js_indicators if kw in code)
        if js_count >= 1:
            return 'javascript'
        
        # Java
        if 'public class' in code or 'System.out' in code or 'public static void' in code:
            return 'java'
        
        # C/C++
        if '#include' in code or 'printf(' in code or 'std::' in code:
            return 'c'
        
        return 'unknown'
    
    def _extract_code_from_response(self, text: str) -> Optional[str]:
        """
        Extrae código de una respuesta de texto.
        Soporta múltiples lenguajes y formatos.
        
        Returns:
            Código extraído o None si no se encontró
        """
        import re
        
        if not text:
            return None
        
        # 1. Buscar bloques de código markdown ```lenguaje\ncódigo```
        code_block_pattern = r'```(?:py|python|javascript|js|html|css|json|md|c|cpp|java|dart)?\s*\n([\s\S]*?)```'
        matches = re.findall(code_block_pattern, text, re.IGNORECASE)
        
        if matches:
            # Retornar el primer bloque de código encontrado
            return matches[0].strip()
        
        # 2. Detectar fragmentos HTML (etiquetas completas)
        html_pattern = r'<(div|span|p|button|input|form|table|h[1-6]|ul|ol|li|a|img|video|audio|canvas|svg|html|head|body)[^>]*>[\s\S]*?<\/\1>'
        html_match = re.search(html_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if html_match:
            return html_match.group(0).strip()
        
        # 3. Detectar estructuras de código por lenguaje
        code_patterns = [
            # Python: funciones, clases, imports
            (r'(?:def |class |import |from )[^\n]+(?:\n(?:    |\t)[^\n]*)*', 'python'),
            # C/C++/Java: includes, main, clases
            (r'(?:#include|public class|int main|void main)[^{]*{[^}]*}', 'c_family'),
            # JavaScript: funciones, const/let/var
            (r'(?:function |const |let |var )[\s\S]*?(?:;|\})', 'javascript'),
        ]
        
        for pattern, lang in code_patterns:
            match = re.search(pattern, text)
            if match:
                matched_text = match.group(0).strip()
                # Solo retornar si parece código real (> 20 chars)
                if len(matched_text) > 20:
                    return matched_text
        
        return None
    
    def _smart_append_code(self, existing_code: str, new_code: str, is_python: bool) -> str:
        """
        Agrega código nuevo al código existente de forma inteligente.
        Preserva todo el código anterior y agrega lo nuevo en la ubicación apropiada.
        
        Args:
            existing_code: Código actual completo
            new_code: Nuevo fragmento a agregar
            is_python: True si es Python, False si es JavaScript
            
        Returns:
            Código combinado
        """
        existing_lines = existing_code.split('\n')
        new_lines = new_code.split('\n')
        
        if is_python:
            # Para Python: encontrar el final del último bloque (función/clase)
            insert_position = len(existing_lines)
            
            # Buscar última línea no vacía
            for i in range(len(existing_lines) - 1, -1, -1):
                line = existing_lines[i].strip()
                if line and not line.startswith('#'):
                    # Si termina con ':', probablemente es inicio de bloque
                    if line.endswith(':'):
                        # Insertar después del bloque completo
                        indent_level = len(existing_lines[i]) - len(existing_lines[i].lstrip())
                        # Buscar siguiente línea con misma indentación o menor
                        for j in range(i + 1, len(existing_lines)):
                            next_line = existing_lines[j]
                            if next_line.strip():  # No vacía
                                next_indent = len(next_line) - len(next_line.lstrip())
                                if next_indent <= indent_level:
                                    insert_position = j
                                    break
                        else:
                            insert_position = len(existing_lines)
                    else:
                        insert_position = i + 1
                    break
            
            # Insertar con separador adecuado
            result_lines = existing_lines[:insert_position] + [''] + new_lines + existing_lines[insert_position:]
            return '\n'.join(result_lines)
        
        else:
            # Para JavaScript: agregar al final con separadores claros
            separator = '\n\n// ' + '='*50 + '\n// NUEVO CÓDIGO AGREGADO\n' + '='*50 + '\n'
            return existing_code + separator + new_code
    
    def _update_stats(self, duration: float, success: bool):
        """Actualiza estadísticas de ejecución"""
        if not success:
            self.execution_stats['errors'] += 1
        
        # Calcular promedio móvil
        total = self.execution_stats['total_requests']
        current_avg = self.execution_stats['avg_response_time']
        self.execution_stats['avg_response_time'] = (
            (current_avg * (total - 1) + duration) / total
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de la capa de orquestación"""
        return {
            **self.execution_stats,
            'registered_agents': list(self.agent_registry.keys()),
            'uptime': 'active'
        }
    
    def _is_simple_request(self, user_input: str) -> bool:
        """Detecta si es un request simple que puede usar fast-path"""
        input_lower = user_input.lower().strip()
        
        # Requests simples: saludos, preguntas cortas, conversacion basica
        simple_patterns = [
            'hola', 'hey', 'buenas', 'hi', 'hello',
            'gracias', 'thanks', 'ok', 'vale',
            'como estas', 'que tal',
            'quien eres', 'que puedes hacer',
            'ayuda', 'help'
        ]
        
        # Si es muy corto (< 20 chars) y no parece generacion de codigo
        if len(user_input.strip()) < 20:
            if not any(word in input_lower for word in ['crear', 'generar', 'codigo', 'code', 'file', 'archivo']):
                return True
        
        # Si coincide con patrones simples
        if any(pattern in input_lower for pattern in simple_patterns):
            return True
        
        return False
    
    def _handle_simple_request(
        self,
        user_input: str,
        session_id: str,
        task_id: str,
        start_time: float,
        task_mgr
    ) -> Dict[str, Any]:
        """Maneja requests simples sin todo el pipeline"""
        try:
            from agent.core.memory_manager import get_memory_manager
            memory_mgr = get_memory_manager()
            
            # Almacenar en memoria (ligero)
            memory_mgr.store(session_id, user_input, role='user')
            
            # Respuestas predefinidas para casos comunes
            input_lower = user_input.lower().strip()
            
            if any(greeting in input_lower for greeting in ['hola', 'hey', 'buenas', 'hi', 'hello']):
                response_text = "¡Hola! ¿En qué puedo ayudarte hoy?"
            elif any(thanks in input_lower for thanks in ['gracias', 'thanks']):
                response_text = "¡De nada! ¿Necesitas algo más?"
            elif 'quien eres' in input_lower or 'que puedes' in input_lower:
                response_text = "Soy Kalin, tu asistente de programación. Puedo generar código, analizar proyectos, corregir errores y mucho más."
            elif any(help_word in input_lower for help_word in ['ayuda', 'help']):
                response_text = "Puedo ayudarte a: crear código, corregir errores, analizar proyectos, refactorizar código. ¿Qué necesitas?"
            else:
                # Para otros casos simples, respuesta genérica rápida
                response_text = "Entendido. ¿Cómo puedo ayudarte?"
            
            # Almacenar respuesta
            memory_mgr.store(session_id, response_text, role='assistant')
            
            duration = time.time() - start_time
            task_mgr.complete_task(task_id, duration)
            
            # Emitir evento ligero
            from agent.core.event_bus import get_event_bus, EVENT_LLM_RESPONSE
            event_bus = get_event_bus()
            event_bus.emit(EVENT_LLM_RESPONSE, {
                'task_id': task_id,
                'session_id': session_id,
                'intention': 'chat',
                'duration': duration,
                'fast_path': True
            }, source='orchestration_layer')
            
            logger.info(f"Simple request handled in {duration:.3f}s (fast-path)")
            
            return {
                'respuesta': response_text,
                'intencion': 'chat',
                'task_id': task_id,
                'session_id': session_id,
                'fast_path': True
            }
        
        except Exception as e:
            # Si falla fast-path, fallback a procesamiento normal
            logger.warning(f"Fast-path failed, falling back to full pipeline: {e}")
            raise
    
    def revert_last_change(self, session_id: str) -> Optional[Dict[str, str]]:
        """
        Revierte el último cambio aplicado en la sesión.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Archivos revertidos o None si no hay snapshots
        """
        if session_id not in self.patch_manager.snapshots:
            logger.warning(f"No snapshots found for session: {session_id}")
            return None
        
        snapshots = self.patch_manager.snapshots[session_id]
        if len(snapshots) < 2:
            logger.warning(f"Not enough snapshots to revert in session: {session_id}")
            return None
        
        # Obtener penúltimo snapshot (el anterior al actual)
        previous_snapshot = snapshots[-2]
        
        logger.info(f"Reverting to snapshot: {previous_snapshot.snapshot_id}")
        return previous_snapshot.files.copy()
    
    def get_change_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """
        Obtiene el historial de cambios aplicados.
        
        Args:
            session_id: ID de la sesión
            limit: Número máximo de cambios a retornar
            
        Returns:
            Lista de cambios con metadata
        """
        patches = self.patch_manager.get_patch_history(session_id, limit)
        
        history = []
        for patch in patches:
            history.append({
                'patch_id': patch.patch_id,
                'timestamp': patch.timestamp,
                'file': patch.file_path,
                'operation': patch.operation.value,
                'description': patch.description,
                'content_preview': patch.content[:100] + '...' if len(patch.content) > 100 else patch.content
            })
        
        return history


# Singleton global
_orchestrator_layer = None


def get_orchestration_layer() -> OrchestrationLayer:
    """Obtiene la instancia singleton de la capa de orquestación"""
    global _orchestrator_layer
    if _orchestrator_layer is None:
        _orchestrator_layer = OrchestrationLayer()
    return _orchestrator_layer
