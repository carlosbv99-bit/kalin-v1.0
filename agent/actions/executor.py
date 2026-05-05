from flask import jsonify
import os
import random
import time
from agent.analyzer import analizar_codigo
from agent.actions.tools.fix_tool import generar_codigo, reparar_codigo
from agent.llm.client import is_available, get_provider_status
from agent.core.state_manager import StateManager
from agent.core.retry_engine import RetryEngine
from agent.core.project_analyzer import ProjectAnalyzer
from agent.actions.strategies import PythonStrategy, ProjectStrategy
from agent.core.logger import get_logger
from agent.core.security import security_manager

logger = get_logger('kalin.executor')

class Executor:
    def __init__(self):
        self.state_manager = StateManager()
        self.retry_engine = RetryEngine()
        self.project_analyzer = None
        self._strategies_cache = {}

    def ejecutar(self, contexto, utils):
        intencion = contexto["intencion"]
        args = contexto.get("args", {})
        
        # Compatibilidad: si viene estado en contexto, actualiza state_manager
        if "estado" in contexto:
            estado = contexto["estado"]
            if "ruta_proyecto" in estado and estado["ruta_proyecto"]:
                self.state_manager.set_ruta(estado["ruta_proyecto"])
        
        ruta_proyecto = self.state_manager.get_ruta()

        if intencion == "setpath":
            ruta = args.get("arg")
            if not ruta:
                return jsonify({"respuesta": "❌ No pude entender la ruta. Usa: /setpath E:\\carpeta o dime 'mi proyecto está en E:\\carpeta'"})
            
            # Si la ruta es solo el disco (ej: "E:\"), pide más información
            if ruta and len(ruta) <= 4:  # Ej: "E:\"
                return jsonify({
                    "respuesta": f"📂 ¿En qué carpeta del disco {ruta}? Por ejemplo:\n"
                                f"`/setpath {ruta}Agente`\n"
                                f"O dime: 'mi proyecto está en el disco E en la carpeta Agente'"
                })
            
            if not self.state_manager.set_ruta(ruta):
                return jsonify({"respuesta": f"❌ Ruta no válida: {ruta}\n\nAsegúrate de que la carpeta exista."})
            
            # Reinitialize project analyzer
            self.project_analyzer = ProjectAnalyzer(ruta)
            self._strategies_cache = {}
            
            return jsonify({"respuesta": f"✅ Proyecto configurado en: {ruta}\n\nAhora puedes decir:\n• 'revisa mi proyecto'\n• 'analiza los archivos'\n• 'hay errores en el código'"})

        if intencion == "scan":
            if not ruta_proyecto:
                return jsonify({"respuesta": "⚠️ Primero usa /setpath"})
            if not self.project_analyzer:
                self.project_analyzer = ProjectAnalyzer(ruta_proyecto)

            return jsonify({
                "respuesta": "📊 Escaneo completado",
                "data": self.project_analyzer.get_resumen()
            })

        if intencion == "apply":
            ultimo_fix = self.state_manager.get_ultimo_fix()
            if not ultimo_fix:
                return jsonify({"respuesta": "❌ No hay cambios pendientes"})

            ruta = ultimo_fix.get("ruta")
            original = ultimo_fix.get("codigo_original")
            nuevo = ultimo_fix.get("codigo_nuevo")
            
            # Validar seguridad de la ruta
            is_safe, error = security_manager.is_safe_path(ruta, ruta_proyecto)
            if not is_safe:
                logger.warning(f"Security violation in apply: {error}")
                return jsonify({"respuesta": error})
            
            # Validar contenido del código
            is_valid, error = security_manager.validate_code_content(nuevo)
            if not is_valid:
                logger.warning(f"Invalid code content: {error}")
                return jsonify({"respuesta": error})

            # Detecta si es diff o código
            es_diff = nuevo.strip().startswith("---") or nuevo.strip().startswith("@@")
            
            if es_diff:
                # Valida que sea diff
                if not (nuevo.count("---") > 0 or nuevo.count("@@") > 0):
                    return jsonify({"respuesta": "❌ Diff inválido"})
            else:
                # Valida que sea código válido
                if not utils["es_codigo_valido"](nuevo):
                    return jsonify({"respuesta": "❌ Código inválido"})

            utils["guardar_backup"](ruta, original)
            utils["escribir_archivo"](ruta, nuevo)
            self.state_manager.clear_ultimo_fix()
            self.state_manager.registrar_exito()
            
            security_manager.log_security_event('apply', f'Changes applied to {ruta}', 'info')
            logger.info(f"Changes applied to {ruta}")
            
            return jsonify({"respuesta": "✅ Cambios aplicados"})

        if intencion == "fix":
            nombre = args.get("arg")
            if not nombre:
                return jsonify({"respuesta": "❌ Usa: /fix archivo"})
            if not ruta_proyecto:
                return jsonify({"respuesta": "⚠️ Primero usa /setpath"})
            if not is_available():
                status = get_provider_status()
                return jsonify({
                    "respuesta": "❌ No hay proveedor LLM disponible. Revisa Ollama local o configura OPENAI_API_KEY/ANTHROPIC_API_KEY.",
                    "status": status
                })

            # Usa project analyzer para búsqueda mejorada
            if not self.project_analyzer:
                self.project_analyzer = ProjectAnalyzer(ruta_proyecto)
            
            ruta_relativa = self.project_analyzer.buscar_archivo(nombre)
            if not ruta_relativa:
                ruta = utils["buscar_archivo_inteligente"](nombre, ruta_proyecto)
            else:
                ruta = os.path.join(ruta_proyecto, ruta_relativa)
            
            if not ruta:
                return jsonify({"respuesta": "❌ Archivo no encontrado"})

            # Leer código
            codigo = utils["leer_archivo"](ruta)
            if not codigo:
                return jsonify({"respuesta": "❌ No se pudo leer el archivo"})
            
            # Validar seguridad
            is_safe, error = security_manager.is_safe_path(ruta, ruta_proyecto)
            if not is_safe:
                logger.warning(f"Security violation: {error}")
                return jsonify({"respuesta": error})

            # Registra último archivo
            self.state_manager.set_ultimo_archivo(ruta, codigo)
            
            # Analizar y reparar
            logger.info(f"Analyzing file: {ruta}")
            analisis = analizar_codigo(codigo)
            logger.debug(f"Analysis completed: {len(analisis)} chars")
            
            nuevo = reparar_codigo(codigo, analisis)

            if not nuevo:
                self.state_manager.registrar_fallo()
                status = get_provider_status()
                logger.error(f"Failed to generate code for {ruta}")
                return jsonify({
                    "respuesta": "❌ No se pudo generar código. Verifica el proveedor LLM configurado.",
                    "preview": "",
                    "status": status
                })

            # Detecta si es diff o código completo
            es_diff = nuevo.strip().startswith("---") or nuevo.strip().startswith("@@")
            
            if es_diff:
                # Es diff: aplica internamente y obtén código nuevo
                print(f"📋 Diff detectado, aplicando...")
                nuevo_limpio = nuevo
                diff = nuevo
                valido = True
            else:
                # Es código: limpia, valida, genera diff
                nuevo_limpio = utils["limpiar_codigo"](nuevo) or nuevo
                valido = utils["es_codigo_valido"](nuevo_limpio)
                diff = utils["generar_diff"](codigo, nuevo_limpio)

            self.state_manager.set_ultimo_fix(ruta, codigo, nuevo_limpio)
            
            logger.info(f"Fix completed for {ruta}: valid={valido}, diff_length={len(diff)}")
            
            return jsonify({
                "respuesta": "⚠️ Modo seguro activo (usa /apply para aplicar cambios)",
                "preview": nuevo_limpio[:800],
                "diff": diff,
                "valido": valido
            })

        if intencion == "analyze":
            nombre = args.get("arg")
            
            # Si no hay archivo específico, haz un scan general
            if not nombre or nombre in ["los archivos", "el código", "el proyecto", "todo"]:
                if not ruta_proyecto:
                    return jsonify({"respuesta": "⚠️ Primero configura la ruta con /setpath"})
                if not self.project_analyzer:
                    self.project_analyzer = ProjectAnalyzer(ruta_proyecto)
                
                resumen = self.project_analyzer.get_resumen()
                respuesta = f"🔍 **Análisis del proyecto:**\n\n"
                respuesta += f"📂 Ruta: {resumen['ruta']}\n"
                respuesta += f"📊 Total archivos: {resumen['total_archivos']}\n"
                respuesta += f"🎯 Tipo principal: {resumen['tipo_principal']}\n\n"
                respuesta += f"📋 Tipos encontrados:\n"
                for tipo, cantidad in resumen['tipos'].items():
                    respuesta += f"• {tipo}: {cantidad} archivos\n"
                respuesta += f"\n💡 Para analizar un archivo específico, dime:\n"
                respuesta += f"'analiza main.py' o 'explica web.py'"
                
                return jsonify({
                    "respuesta": respuesta,
                    "data": resumen
                })
            
            if not ruta_proyecto:
                return jsonify({"respuesta": "⚠️ Primero usa /setpath"})
            if not is_available():
                status = get_provider_status()
                return jsonify({
                    "respuesta": "❌ No hay proveedor LLM disponible. Revisa Ollama local o configura OPENAI_API_KEY/ANTHROPIC_API_KEY.",
                    "status": status
                })

            ruta = utils["buscar_archivo_inteligente"](nombre, ruta_proyecto)
            if not ruta:
                return jsonify({"respuesta": f"❌ Archivo '{nombre}' no encontrado"})
            
            # Validar seguridad
            is_safe, error = security_manager.is_safe_path(ruta, ruta_proyecto)
            if not is_safe:
                logger.warning(f"Security violation in analyze: {error}")
                return jsonify({"respuesta": error})

            codigo = utils["leer_archivo"](ruta)
            if not codigo:
                return jsonify({"respuesta": "❌ No se pudo leer el archivo"})

            analisis = analizar_codigo(codigo)
            logger.info(f"Analysis completed for {os.path.basename(ruta)}")
            return jsonify({
                "respuesta": f"🔍 **Análisis de {os.path.basename(ruta)}:**\n\n{analisis}"
            })

        if intencion == "create":
            prompt = args.get("texto")
            if not prompt:
                prompt = contexto.get("mensaje")
            if not is_available():
                status = get_provider_status()
                return jsonify({
                    "respuesta": "❌ No hay proveedor LLM disponible. Revisa Ollama local o configura OPENAI_API_KEY/ANTHROPIC_API_KEY.",
                    "status": status
                })

            nuevo = generar_codigo(prompt)
            if not nuevo:
                return jsonify({"respuesta": "❌ No se pudo generar código. Verifica el proveedor LLM configurado y el estado del servidor.", "preview": ""})

            return jsonify({"respuesta": "✅ Código generado", "preview": nuevo[:800]})

        if intencion == "refactor":
            nombre = args.get("arg")
            if not nombre:
                return jsonify({"respuesta": "❌ Usa: /refactor archivo"})
            if not ruta_proyecto:
                return jsonify({"respuesta": "⚠️ Primero usa /setpath"})
            if not is_available():
                status = get_provider_status()
                return jsonify({
                    "respuesta": "❌ No hay proveedor LLM disponible. Revisa Ollama local o configura OPENAI_API_KEY/ANTHROPIC_API_KEY.",
                    "status": status
                })

            ruta = utils["buscar_archivo_inteligente"](nombre, ruta_proyecto)
            if not ruta:
                return jsonify({"respuesta": "❌ Archivo no encontrado"})
            
            # Validar seguridad
            is_safe, error = security_manager.is_safe_path(ruta, ruta_proyecto)
            if not is_safe:
                logger.warning(f"Security violation in refactor: {error}")
                return jsonify({"respuesta": error})

            codigo = utils["leer_archivo"](ruta)
            if not codigo:
                return jsonify({"respuesta": "❌ No se pudo leer el archivo"})

            analisis = analizar_codigo(codigo)
            nuevo = reparar_codigo(codigo, analisis)
            if not nuevo:
                logger.error(f"Failed to refactor {ruta}")
                return jsonify({"respuesta": "❌ No se pudo refactorizar el código.", "preview": ""})

            diff = utils["generar_diff"](codigo, nuevo)
            
            logger.info(f"Refactor completed for {ruta}")
            
            return jsonify({
                "respuesta": "♻️ Refactorización propuesta",
                "preview": nuevo[:800],
                "diff": diff,
                "valido": utils["es_codigo_valido"](nuevo)
            })

        if intencion == "help":
            logger.info("Help command executed")
            return jsonify({
                "respuesta": "Comandos disponibles: /setpath <ruta>, /scan, /fix <archivo>, /apply, /analyze <archivo>, /create <requerimiento>, /refactor <archivo>"
            })

        if intencion == "greeting" or intencion == "chat":
            from agent.llm.client import generate
            
            mensaje_usuario = contexto.get("mensaje", "")
            
            if not is_available():
                return jsonify({
                    "respuesta": "⚠️ No hay IA disponible. Asegúrate de que Ollama esté corriendo con: ollama serve"
                })
            
            # PROMPTS ESPECIALIZADOS POR MODO
            prompt_chat = """Eres Kalin, un asistente conversacional único y dinámico.

IMPORTANTE: Cada respuesta debe ser DIFERENTE y contextual. NUNCA repitas frases.

TU PERSONALIDAD:
- Entusiasta sobre tecnología y desarrollo
- Curioso por conocer los proyectos del usuario
- Proactivo en sugerir ideas
- Conversacional, no robótico

CÓMO RESPONDER SEGÚN EL CONTEXTO:

1. SALUDOS ("hola", "buenas", etc.):
   - Varía tu saludo cada vez
   - Haz una pregunta diferente sobre su proyecto actual
   - Ejemplos variados:
     * "¡Hey! ¿Qué estás construyendo hoy?"
     * "¡Buenas! ¿En qué proyecto trabajas ahora?"
     * "¡Hola! ¿Tienes alguna idea interesante en mente?"

2. IDEAS DE PROYECTOS ("quiero una app de...", "necesito crear..."):
   - Muestra entusiasmo genuino
   - Haz 2-3 preguntas específicas sobre el proyecto
   - Sugiere tecnologías relevantes
   - NO listes comandos técnicos
   - Ejemplo: "¡Una app de agenda multiusuario suena genial! ¿La imaginas con sincronización en tiempo real? ¿Para Android nativo o Flutter? Cuéntame más detalles."

3. PREGUNTAS SOBRE CAPACIDADES ("qué puedes hacer", "puedes escribir código"):
   - Explica de forma natural tus habilidades
   - Menciona ejemplos concretos
   - Invita a empezar algo
   - Ejemplo: "¡Claro! Puedo ayudarte a crear apps Android, debuggear código, analizar proyectos... ¿Quieres que empecemos con algo específico?"

4. SOLICITUDES DE CÓDIGO ("dame código", "muéstrame el código", "escribe código"):
   - CONFIRMA qué tipo de código necesita
   - Pide detalles específicos del requerimiento
   - Una vez claro, genera el código usando el backend
   - Presenta el código de forma clara

REGLAS CRÍTICAS:
- NUNCA uses la misma frase dos veces
- NUNCA listes comandos (/setpath, /create, etc.) a menos que te lo pidan explícitamente
- Mantén respuestas de 2-4 oraciones
- Termina con una pregunta o invitación a continuar
- Sé específico, no genérico"""

            prompt_greeting = """Eres Kalin, un asistente cálido y dinámico.

Saluda de forma ÚNICA cada vez. Varía entre:
- "¡Hey! ¿Qué estás construyendo hoy?"
- "¡Buenas! Soy Kalin, tu asistente de desarrollo. ¿En qué proyecto trabajas?"
- "¡Hola! ¿Tienes alguna idea interesante en mente?"
- "¡Qué tal! Estoy listo para ayudarte con tu próximo proyecto."

Menciona brevemente que puedes ayudar con apps Android, Python, web, debugging. Termina con una pregunta específica sobre lo que está haciendo."""

            # Seleccionar prompt según tipo
            if intencion == "greeting":
                prompt_sistema = prompt_greeting
            else:
                prompt_sistema = prompt_chat
            
            # Agregar variación contextual para evitar respuestas repetitivas
            timestamp = time.strftime("%H:%M")
            variacion = random.randint(1, 1000)
            contexto_extra = f"\n\n[Contexto: Son las {timestamp}. ID de conversación: {variacion}. Cada respuesta debe ser ÚNICA.]"
            
            prompt_completo = f"""{prompt_sistema}{contexto_extra}

Mensaje del usuario: {mensaje_usuario}

Tu respuesta:"""
            
            try:
                # DETECTAR si el usuario está pidiendo código explícitamente
                mensaje_lower = mensaje_usuario.lower()
                pide_codigo = any(frase in mensaje_lower for frase in [
                    "dame el codigo", "dame codigo", "muestrame el codigo", 
                    "escribe codigo", "genera codigo", "codigo para",
                    "quiero el codigo", "necesito codigo", "crea el codigo"
                ])
                
                # Si pide código, generar con DeepSeek y VALIDAR con Llama
                if pide_codigo and len(mensaje_usuario) > 15:
                    from agent.actions.tools.fix_tool import generar_codigo
                    from agent.llm.client import generate as generate_llm
                    
                    requerimiento = mensaje_usuario
                    
                    try:
                        # Intentar generar código (SOLO 1 intento para velocidad)
                        print(f"⚙️ Generando código con DeepSeek...")
                        codigo_generado = generar_codigo(requerimiento, max_intentos=1)
                        
                        print(f"🔍 DEBUG - Código generado: {len(codigo_generado) if codigo_generado else 0} chars")
                        
                        if codigo_generado and len(codigo_generado) > 20:
                            # VALIDAR calidad del código con Llama
                            print(f"✅ Código generado, validando calidad...")
                            
                            prompt_validacion = f"""Eres un supervisor de calidad de código.

Evalúa este código y determina si es ACEPTABLE para mostrar al usuario:

CÓDIGO:
{codigo_generado[:500]}

CRITERIOS MÍNIMOS:
- Contiene código válido (import/def/class/etc)
- No está completamente vacío
- Tiene estructura lógica básica

IGNORA:
- Comentarios explicativos menores
- Texto introductorio breve
- Formato imperfecto

Responde SOLO "APROBADO" si el código es usable, o "RECHAZADO" si está completamente mal."""
                            
                            validacion = generate_llm(prompt_validacion, max_tokens=20, use_case="chat")
                            
                            # DEBUG: Mostrar respuesta completa de validación
                            print(f"🔍 DEBUG - Respuesta de validación: '{validacion}'")
                            print(f"🔍 DEBUG - Longitud: {len(validacion) if validacion else 0} chars")
                            
                            if validacion and len(validacion.strip()) > 0:
                                validacion_upper = validacion.upper().strip()
                                print(f"🔍 DEBUG - Validación normalizada: '{validacion_upper}'")
                                
                                # Verificar si contiene APROBADO (más flexible)
                                if "APROBADO" in validacion_upper or "ACEPTADO" in validacion_upper or "OK" in validacion_upper:
                                    print(f"✅ Código APROBADO")
                                    respuesta_ia = f"```\n{codigo_generado}\n```"
                                else:
                                    print(f"❌ Código RECHAZADO - Razón: {validacion}")
                                    respuesta_ia = "El código generado no cumple los estándares de calidad. ¿Puedes especificar mejor qué necesitas?"
                            else:
                                print(f"❌ Validación fallida - respuesta vacía o None")
                                respuesta_ia = "Error al validar el código generado."
                        else:
                            print(f"❌ Código NO generado o muy corto")
                            respuesta_ia = "No pude generar código. ¿Puedes ser más específico?"
                        
                    except Exception as e:
                        print(f"❌ ERROR en generación/validación: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        respuesta_ia = f"Error interno al generar código: {str(e)}"
                    
                    return jsonify({"respuesta": respuesta_ia})
                
                # Para conversaciones normales, usar Llama
                respuesta_ia = generate(prompt_completo, max_tokens=300, use_case="chat")
                if not respuesta_ia or len(respuesta_ia.strip()) < 10:
                    respuesta_ia = f"👋 ¡Hola! Soy Kalin, tu asistente de desarrollo. ¿En qué puedo ayudarte hoy?"
                
                return jsonify({"respuesta": respuesta_ia})
            except Exception as e:
                return jsonify({
                    "respuesta": f"❌ Error al procesar: {str(e)}"
                })


        return jsonify({"respuesta": "❓ Acción no soportada"})

    def _get_strategy(self, tipo: str):
        """Obtiene o crea una estrategia según el tipo"""
        if tipo in self._strategies_cache:
            return self._strategies_cache[tipo]

        ruta_proyecto = self.state_manager.get_ruta()
        
        if tipo == "python":
            estrategia = PythonStrategy(self.retry_engine)
        elif tipo == "project":
            if not ruta_proyecto:
                estrategia = PythonStrategy(self.retry_engine)
            else:
                estrategia = ProjectStrategy(self.retry_engine, ruta_proyecto)
        else:
            estrategia = PythonStrategy(self.retry_engine)

        self._strategies_cache[tipo] = estrategia
        return estrategia

    def _detectar_tipo_archivo(self, ruta_archivo: str) -> str:
        """Detecta el tipo de archivo por su extensión"""
        ext = os.path.splitext(ruta_archivo)[1].lower()

        tipos = {
            ".py": "python",
            ".dart": "flutter",
            ".kt": "kotlin",
            ".java": "java",
            ".js": "javascript",
            ".ts": "typescript",
        }

        return tipos.get(ext, "unknown")
