from flask import jsonify
import os
import random
import time
from agent.analyzer import analizar_codigo
from agent.actions.tools.fix_tool import reparar_codigo
from agent.actions.tools import fix_tool  # Para generar_codigo
from agent.llm.client import is_available, get_provider_status
from agent.core.state_manager import StateManager
from agent.core.retry_engine import RetryEngine
from agent.core.project_analyzer import ProjectAnalyzer
from agent.core.experience_memory import get_experience_memory
from agent.core.conversation_memory import conversation_memory as conv_mem_instance
from agent.actions.strategies import PythonStrategy, ProjectStrategy
from agent.core.logger import get_logger
from agent.core.security import security_manager

logger = get_logger('kalin.executor')

class Executor:
    def __init__(self):
        self.state_manager = StateManager()
        self.retry_engine = RetryEngine()
        self.experience_memory = get_experience_memory()
        self.conversation_memory = conv_mem_instance  # Usar instancia global
        self.project_analyzer = None
        self._strategies_cache = {}

    def ejecutar(self, contexto, utils):
        intencion = contexto["intencion"]
        args = contexto.get("args", {})
        
        # INFERIR CONTEXTO FALTANTE usando memoria conversacional
        mensaje_usuario = contexto.get("mensaje", "")
        improved_args = self.conversation_memory.infer_missing_context(
            mensaje=mensaje_usuario,
            detected_intention=intencion,
            args=args
        )
        
        # Usar argumentos mejorados si se infirió contexto
        if improved_args != args:
            logger.info(f"Context inferred: {improved_args}")
            args = improved_args
            contexto["args"] = args
        
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
            
            # ACTUALIZAR MEMORIA CONVERSACIONAL
            self.conversation_memory.update_context(
                intention="setpath",
                args={"arg": ruta},
                result=f"Project path set to {ruta}",
                metadata={"project_path": ruta}
            )
            
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
            
            # Consultar experiencia previa para mejor estrategia
            file_type = os.path.splitext(ruta)[1].lstrip('.')
            strategy_recommendation = self.experience_memory.get_best_strategy(
                task_type='fix',
                file_type=file_type,
                problem_description=f"Fix errors in {os.path.basename(ruta)}"
            )
            
            if strategy_recommendation:
                logger.info(f"Experience recommendation: {strategy_recommendation['recommendation']}")
            
            # Analizar y reparar
            logger.info(f"Analyzing file: {ruta}")
            start_time = time.time()
            analisis = analizar_codigo(codigo)
            logger.debug(f"Analysis completed: {len(analisis)} chars")
            
            nuevo = reparar_codigo(codigo, analisis)
            duration = time.time() - start_time

            if not nuevo:
                # Registrar experiencia fallida
                self.experience_memory.record_experience(
                    task_type='fix',
                    problem_description=f"Failed to fix {os.path.basename(ruta)}",
                    file_type=file_type,
                    strategy_used='default',
                    success=False,
                    confidence_score=0.0,
                    duration_seconds=duration,
                    error_message='No code generated'
                )
                
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
            
            # Registrar experiencia exitosa
            self.experience_memory.record_experience(
                task_type='fix',
                problem_description=f"Fixed errors in {os.path.basename(ruta)}",
                file_type=file_type,
                strategy_used=strategy_recommendation['strategy'] if strategy_recommendation else 'default',
                success=True,
                confidence_score=0.8 if valido else 0.5,
                duration_seconds=duration,
                solution_summary=f"Applied fix to {os.path.basename(ruta)}"
            )
            
            # ACTUALIZAR MEMORIA CONVERSACIONAL
            self.conversation_memory.update_context(
                intention="fix",
                args={"arg": ruta},
                result=nuevo_limpio[:500] if nuevo_limpio else None,
                metadata={
                    "duration": duration,
                    "file_type": file_type,
                    "valid": valido
                }
            )
            
            logger.info(f"Fix completed for {ruta}: valid={valido}, diff_length={len(diff)}, experience_recorded=True")
            
            return jsonify({
                "respuesta": "⚠️ Modo seguro activo (usa /apply para aplicar cambios)",
                "preview": nuevo_limpio[:800],
                "diff": diff,
                "valido": valido
            })

        if intencion == "analyze":
            nombre = args.get("arg")
            mensaje_original = contexto.get("mensaje", "")
            
            # VERIFICAR SI HAY CÓDIGO PEGADO DIRECTAMENTE EN EL MENSAJE
            import re
            code_blocks = re.findall(r'```(?:\w+)?\s*\n(.*?)\n```', mensaje_original, re.DOTALL)
            
            if code_blocks:
                # Hay código pegado, analizarlo directamente
                codigo = code_blocks[0]  # Tomar primer bloque
                
                # Detectar lenguaje del bloque de código
                lang_match = re.search(r'```(\w+)', mensaje_original)
                language = lang_match.group(1) if lang_match else "unknown"
                
                # Verificar si el código está completo
                def is_code_truncated(code):
                    """Detecta si el código está truncado/incompleto"""
                    lines = code.strip().split('\n')
                    if not lines:
                        return True
                    
                    last_line = lines[-1].strip()
                    
                    # Patrones de código incompleto
                    incomplete_patterns = [
                        r'if\s*\($',           # if ( sin cerrar
                        r'for\s*\(',           # for ( sin cerrar
                        r'while\s*\(',         # while ( sin cerrar
                        r'def\s+\w+\([^)]*$',  # def func( sin cerrar
                        r'class\s+\w+\([^)]*$', # class X( sin cerrar
                        r'=>\s*$',             # => sin cuerpo (Dart/JS)
                    ]
                    
                    for pattern in incomplete_patterns:
                        if re.search(pattern, last_line):
                            return True
                    
                    # Verificar balance de llaves/paréntesis
                    open_braces = code.count('{') - code.count('}')
                    open_parens = code.count('(') - code.count(')')
                    
                    if open_braces > 2 or open_parens > 2:  # Margen de tolerancia
                        return True
                    
                    return False
                
                if is_code_truncated(codigo):
                    # Obtener última línea completa
                    lines = codigo.strip().split('\n')
                    last_lines = '\n'.join(lines[-3:]) if len(lines) >= 3 else codigo
                    
                    return jsonify({
                        "respuesta": f"⚠️ **El código proporcionado parece estar incompleto o truncado.**\n\n"
                                   f"Por favor, proporciona el código COMPLETO para poder analizarlo correctamente.\n\n"
                                   f"**El código se corta en:**\n```\n{last_lines}\n```\n\n"
                                   f"💡 Consejo: Copia y pega todo el archivo, no solo una parte."
                    })
                
                # Analizar código directamente
                contexto_analisis = {
                    "user_message": contexto.get("mensaje", "Analiza este código"),
                    "project_type": language,
                    "files": [f"code_snippet.{language}"],
                    "conversation_history": True,
                    "is_inline_code": True  # Flag para indicar que es código pegado
                }
                
                start_time = time.time()
                analisis = analizar_codigo(codigo, contexto=contexto_analisis)
                duration = time.time() - start_time
                logger.info(f"Inline code analysis completed ({language}, {len(codigo)} chars)")
                
                # Guardar en memoria conversacional
                self.conversation_memory.update_context(
                    intention="analyze",
                    args={"source": "inline_code", "language": language},
                    result=analisis,
                    metadata={
                        "duration": duration,
                        "file_type": language,
                        "code_length": len(codigo)
                    }
                )
                
                return jsonify({
                    "respuesta": f"🔍 **Análisis del código proporcionado:**\n\n{analisis}"
                })
            
            # Si no hay código pegado, continuar con búsqueda de archivo normal
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
            
            # VERIFICAR SI HAY RUTA DE PROYECTO EN LOS ARGUMENTOS (extraída del mensaje)
            project_path_from_msg = args.get("project_path")
            if project_path_from_msg:
                # Usar la ruta mencionada en el mensaje
                ruta_proyecto_actual = project_path_from_msg
                logger.info(f"Using project path from message: {ruta_proyecto_actual}")
            else:
                # Usar ruta configurada
                ruta_proyecto_actual = ruta_proyecto
            
            if not ruta_proyecto_actual:
                return jsonify({"respuesta": "⚠️ Primero usa /setpath o menciona la ruta en tu mensaje"})
            
            if not is_available():
                status = get_provider_status()
                return jsonify({
                    "respuesta": "❌ No hay proveedor LLM disponible. Revisa Ollama local o configura OPENAI_API_KEY/ANTHROPIC_API_KEY.",
                    "status": status
                })

            # Inicializar project analyzer con la ruta correcta
            if not self.project_analyzer or self.project_analyzer.ruta != ruta_proyecto_actual:
                self.project_analyzer = ProjectAnalyzer(ruta_proyecto_actual)
            
            ruta = utils["buscar_archivo_inteligente"](nombre, ruta_proyecto_actual)
            if not ruta:
                # Proporcionar información útil sobre archivos disponibles
                logger.warning(f"File '{nombre}' not found in {ruta_proyecto_actual}")
                
                # Intentar encontrar archivos similares
                if self.project_analyzer:
                    archivos_similares = [
                        arch for arch in self.project_analyzer.archivos.keys()
                        if nombre.lower() in arch.lower()
                    ]
                    
                    if archivos_similares:
                        sugerencias = ", ".join(archivos_similares[:5])
                        return jsonify({
                            "respuesta": f"❌ Archivo '{nombre}' no encontrado en {ruta_proyecto_actual}\n\n"
                                       f"💡 Archivos similares encontrados:\n"
                                       f"{chr(10).join('• ' + a for a in archivos_similares[:5])}"
                        })
                    else:
                        # Mostrar algunos archivos disponibles del mismo tipo
                        ext = os.path.splitext(nombre)[1].lower()
                        tipo_hint = {
                            '.py': 'python',
                            '.dart': 'flutter',
                            '.java': 'java',
                            '.js': 'javascript',
                            '.json': None  # JSON no tiene tipo específico
                        }.get(ext)
                        
                        if tipo_hint:
                            archivos_tipo = self.project_analyzer.get_archivos_por_tipo(tipo_hint)[:5]
                            if archivos_tipo:
                                return jsonify({
                                    "respuesta": f"❌ Archivo '{nombre}' no encontrado en {ruta_proyecto_actual}\n\n"
                                               f"📂 Archivos {tipo_hint} disponibles:\n"
                                               f"{chr(10).join('• ' + a for a in archivos_tipo)}"
                                })
                
                return jsonify({"respuesta": f"❌ Archivo '{nombre}' no encontrado en {ruta_proyecto_actual}"})
            
            # Validar seguridad
            is_safe, error = security_manager.is_safe_path(ruta, ruta_proyecto_actual)
            if not is_safe:
                logger.warning(f"Security violation in analyze: {error}")
                return jsonify({"respuesta": error})

            codigo = utils["leer_archivo"](ruta)
            if not codigo:
                return jsonify({"respuesta": "❌ No se pudo leer el archivo"})

            # Construir contexto para prompt dinámico
            contexto_analisis = {
                "user_message": contexto.get("mensaje", "Analiza este código"),
                "project_type": None,  # Se detectará automáticamente
                "files": [os.path.basename(ruta)],
                "conversation_history": True
            }
            
            start_time = time.time()
            analisis = analizar_codigo(codigo, contexto=contexto_analisis)
            duration = time.time() - start_time
            logger.info(f"Analysis completed for {os.path.basename(ruta)}")
            
            # Detectar tipo de archivo
            file_type = os.path.splitext(ruta)[1].lstrip('.')
            
            # GUARDAR EN MEMORIA CONVERSACIONAL
            self.conversation_memory.update_context(
                intention="analyze",
                args={"arg": os.path.basename(ruta)},
                result=analisis,
                metadata={
                    "duration": duration,
                    "file_type": file_type,
                    "project_path": ruta_proyecto_actual
                }
            )
            
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

            # Detectar tipo de archivo/lenguaje solicitado
            lenguajes_posibles = {
                'python': 'py', 'py': 'py',
                'javascript': 'js', 'js': 'js',
                'typescript': 'ts', 'ts': 'ts',
                'html': 'html', 'css': 'css',
                'java': 'java', 'c++': 'cpp', 'cpp': 'cpp',
                'c#': 'cs', 'csharp': 'cs',
                'ruby': 'rb', 'go': 'go', 'rust': 'rs'
            }
            
            file_type = 'py'  # default
            prompt_lower = prompt.lower()
            for key, value in lenguajes_posibles.items():
                if key in prompt_lower:
                    file_type = value
                    break
            
            # Consultar experiencia previa
            strategy_recommendation = self.experience_memory.get_best_strategy(
                task_type='create',
                file_type=file_type,
                problem_description=prompt[:100]
            )
            
            if strategy_recommendation:
                logger.info(f"Experience recommendation for create: {strategy_recommendation['recommendation']}")
            
            start_time = time.time()
            nuevo = fix_tool.generar_codigo(prompt)
            duration = time.time() - start_time
            
            if not nuevo:
                # Registrar experiencia fallida
                self.experience_memory.record_experience(
                    task_type='create',
                    problem_description=f"Failed to create code: {prompt[:100]}",
                    file_type=file_type,
                    strategy_used='default',
                    success=False,
                    confidence_score=0.0,
                    duration_seconds=duration,
                    error_message='No code generated'
                )
                
                # Guardar memoria en disco inmediatamente
                self.experience_memory.save()
                
                return jsonify({"respuesta": "❌ No se pudo generar código. Verifica el proveedor LLM configurado y el estado del servidor.", "preview": ""})

            # Guardar el código generado en state_manager para poder mostrarlo después
            self.state_manager.set_ultimo_codigo_generado(nuevo)
            
            # Registrar experiencia exitosa
            self.experience_memory.record_experience(
                task_type='create',
                problem_description=f"Created {file_type} code: {prompt[:100]}",
                file_type=file_type,
                strategy_used=strategy_recommendation['strategy'] if strategy_recommendation else 'default',
                success=True,
                confidence_score=0.85,
                duration_seconds=duration,
                solution_summary=f"Generated {len(nuevo)} chars of {file_type} code"
            )
            
            # ACTUALIZAR MEMORIA CONVERSACIONAL
            self.conversation_memory.update_context(
                intention="create",
                args={"texto": prompt, "file_type": file_type},
                result=nuevo,  # Pasar el código completo, no solo un resumen
                metadata={
                    "duration": duration,
                    "code_length": len(nuevo),
                    "file_type": file_type
                }
            )
            
            # Guardar memoria en disco inmediatamente
            self.experience_memory.save()
            
            logger.info(f"Create completed: type={file_type}, length={len(nuevo)}, experience_recorded=True")
            
            # Mostrar el CÓDIGO FUENTE automáticamente (no compilado)
            lenguaje_display = file_type.upper() if len(file_type) <= 3 else file_type.capitalize()
            
            # jsonify escapará automáticamente los caracteres especiales
            respuesta_texto = f"✅ Código {lenguaje_display} generado exitosamente:\n\n```{file_type}\n{nuevo}\n```"
            
            # DEBUG: Verificar longitud
            logger.info(f"Returning response with code length: {len(nuevo)} chars")
            
            return jsonify({"respuesta": respuesta_texto, "preview": nuevo[:800]})

        if intencion == "show_code":
            # Mostrar último código generado
            codigo = self.state_manager.get_ultimo_codigo_generado()
            if not codigo:
                return jsonify({"respuesta": "❌ No hay código generado recientemente. Usa /create para generar código."})
            
            # Detectar si el usuario quiere el código sin comentarios
            mensaje = contexto.get("mensaje", "").lower()
            sin_comentarios = any(frase in mensaje for frase in [
                "sin comentarios", "quitar comentarios", "eliminar comentarios",
                "no comentarios", "solo código", "solo codigo"
            ])
            
            if sin_comentarios:
                # Eliminar comentarios del código
                import re
                lineas = codigo.split('\n')
                lineas_sin_comentarios = []
                for linea in lineas:
                    # Eliminar comentarios de línea (# ...)
                    linea_limpia = re.sub(r'#.*$', '', linea).rstrip()
                    if linea_limpia:  # Solo agregar líneas no vacías
                        lineas_sin_comentarios.append(linea_limpia)
                codigo_mostrar = '\n'.join(lineas_sin_comentarios)
                respuesta = f"📄 **Código limpio (sin comentarios):**\n\n```python\n{codigo_mostrar}\n```"
            else:
                # Mostrar código formateado con mensaje útil
                respuesta = f"📄 **Código generado:**\n\n```python\n{codigo}\n```\n\n💡 Código listo para copiar y usar. ¿Necesitas que lo guarde en un archivo o que modifique algo?"
            
            return jsonify({"respuesta": respuesta})

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

            # Construir contexto para prompt dinámico
            contexto_refactor = {
                "user_message": contexto.get("mensaje", "Refactoriza este código"),
                "project_type": None,
                "files": [os.path.basename(ruta)],
                "conversation_history": True
            }
            
            analisis = analizar_codigo(codigo, contexto=contexto_refactor)
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
                "respuesta": "Comandos disponibles: /setpath <ruta>, /scan, /fix <archivo>, /apply, /analyze <archivo>, /create <requerimiento>, /refactor <archivo>, /experience, /learn"
            })

        if intencion == "experience" or (intencion == "chat" and any(word in contexto.get("mensaje", "").lower() for word in ["experiencia", "aprendizaje", "memoria", "estadísticas"])):
            # Mostrar resumen de experiencia
            summary = self.experience_memory.get_learning_summary()
            
            respuesta = f"🧠 **Memoria de Aprendizaje**\n\n"
            respuesta += f"📊 Experiencias totales: {summary['total_experiences']}\n"
            respuesta += f"✅ Éxitos: {summary['total_successes']}\n"
            respuesta += f"❌ Fallos: {summary['total_failures']}\n"
            respuesta += f"📈 Tasa de éxito global: {summary['overall_success_rate']:.1%}\n\n"
            
            if summary['success_rate_by_type']:
                respuesta += "🎯 Por tipo de tarea:\n"
                for task_type, stats in summary['success_rate_by_type'].items():
                    respuesta += f"• {task_type}: {stats.get('rate', 0):.1%} éxito ({stats.get('total', 0)} intentos)\n"
                respuesta += "\n"
            
            if summary['patterns_detected'] > 0:
                respuesta += f"🔍 Patrones detectados: {summary['patterns_detected']}\n\n"
            
            if summary['top_insights']:
                respuesta += "💡 Insights:\n"
                for insight in summary['top_insights'][:3]:
                    respuesta += f"• {insight['message']}\n"
                respuesta += "\n"
            
            if summary['recommendations']:
                respuesta += "📝 Recomendaciones:\n"
                for rec in summary['recommendations'][:2]:
                    respuesta += f"• {rec}\n"
            
            return jsonify({"respuesta": respuesta})

        if intencion == "learn" or (intencion == "chat" and any(word in contexto.get("mensaje", "").lower() for word in ["patrones", "qué has aprendido", "qué sabes"])):
            # Mostrar patrones aprendidos
            patterns = self.experience_memory.get_patterns()
            
            if not patterns:
                return jsonify({
                    "respuesta": "🧠 Aún no he detectado patrones. Sigue usando Kalin para que pueda aprender de la experiencia."
                })
            
            respuesta = f"🔍 **Patrones Aprendidos** ({len(patterns)})\n\n"
            
            for i, pattern in enumerate(patterns[:5], 1):
                respuesta += f"{i}. {pattern.description}\n"
                respuesta += f"   Frecuencia: {pattern.frequency} veces\n"
                respuesta += f"   Éxito: {pattern.success_rate:.1%}\n"
                respuesta += f"   💡 {pattern.recommended_action}\n\n"
            
            if len(patterns) > 5:
                respuesta += f"...y {len(patterns) - 5} patrones más\n"
            
            return jsonify({"respuesta": respuesta})

        if intencion == "export_experience" or (intencion == "chat" and any(word in contexto.get("mensaje", "").lower() for word in ["exportar experiencia", "exportar memoria", "compartir aprendizaje"])):
            # Exportar experiencias a archivo JSON
            import json
            from datetime import datetime
            
            try:
                # Crear paquete de exportación
                export_data = {
                    'version': '1.0',
                    'exported_at': datetime.now().isoformat(),
                    'experiences': [exp.to_dict() for exp in self.experience_memory.experiences],
                    'patterns': {k: v.to_dict() for k, v in self.experience_memory.patterns.items()},
                    'statistics': self.experience_memory.statistics
                }
                
                # Guardar en archivo con timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"kalin_experience_{timestamp}.json"
                filepath = os.path.join(os.getcwd(), filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                num_experiences = len(export_data['experiences'])
                num_patterns = len(export_data['patterns'])
                
                respuesta = f"📦 **Experiencia exportada exitosamente**\n\n"
                respuesta += f"📄 Archivo: `{filename}`\n"
                respuesta += f"📍 Ubicación: `{filepath}`\n\n"
                respuesta += f"📊 Contenido:\n"
                respuesta += f"• {num_experiences} experiencias\n"
                respuesta += f"• {num_patterns} patrones aprendidos\n\n"
                respuesta += f"💡 Comparte este archivo con otros usuarios de Kalin para que puedan importar tu experiencia."
                
                logger.info(f"Experience exported to {filepath}")
                return jsonify({"respuesta": respuesta})
            
            except Exception as e:
                logger.error(f"Error exporting experience: {e}")
                return jsonify({"respuesta": f"❌ Error al exportar: {str(e)}"})

        if intencion == "import_experience" or (intencion == "chat" and any(word in contexto.get("mensaje", "").lower() for word in ["importar experiencia", "importar memoria", "cargar aprendizaje"])):
            # Importar experiencias desde archivo JSON
            import json
            
            try:
                # Buscar archivo en el mensaje o usar el más reciente
                mensaje = contexto.get("mensaje", "")
                
                # Extraer ruta del archivo si se proporcionó
                import re
                match = re.search(r'[E-Z]:\\[\w\\ ]+\.json', mensaje, re.IGNORECASE)
                if match:
                    filepath = match.group(0)
                else:
                    # Buscar el archivo más reciente en el directorio actual
                    import glob
                    files = glob.glob("kalin_experience_*.json")
                    if not files:
                        return jsonify({"respuesta": "❌ No se encontró archivo de experiencia. Usa: importar experiencia E:\\ruta\\archivo.json"})
                    
                    # Usar el archivo más reciente
                    filepath = max(files, key=os.path.getctime)
                
                if not os.path.exists(filepath):
                    return jsonify({"respuesta": f"❌ Archivo no encontrado: {filepath}"})
                
                # Cargar datos
                with open(filepath, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)
                
                # Validar estructura
                if 'experiences' not in import_data:
                    return jsonify({"respuesta": "❌ Archivo inválido: no contiene experiencias"})
                
                # Contar experiencias actuales
                current_count = len(self.experience_memory.experiences)
                
                # Importar experiencias (evitar duplicados por ID)
                existing_ids = {exp.experience_id for exp in self.experience_memory.experiences}
                new_count = 0
                
                from agent.core.experience_memory import Experience
                for exp_data in import_data['experiences']:
                    if exp_data.get('experience_id') not in existing_ids:
                        try:
                            exp = Experience.from_dict(exp_data)
                            self.experience_memory.experiences.append(exp)
                            existing_ids.add(exp.experience_id)
                            new_count += 1
                        except Exception as e:
                            logger.warning(f"Error importing experience: {e}")
                
                # Actualizar índices
                self.experience_memory._rebuild_indices()
                
                # Guardar memoria actualizada
                self.experience_memory.save()
                
                total_count = len(self.experience_memory.experiences)
                
                respuesta = f"✅ **Experiencia importada exitosamente**\n\n"
                respuesta += f"📄 Archivo: `{os.path.basename(filepath)}`\n\n"
                respuesta += f"📊 Resultados:\n"
                respuesta += f"• {new_count} experiencias nuevas importadas\n"
                respuesta += f"• {current_count} experiencias previas\n"
                respuesta += f"• {total_count} experiencias totales\n\n"
                
                if new_count > 0:
                    respuesta += f"🧠 Kalin ahora es más inteligente con {new_count} nuevas experiencias aprendidas."
                else:
                    respuesta += f"ℹ️  Todas las experiencias ya estaban en la memoria (sin duplicados)."
                
                logger.info(f"Experience imported: {new_count} new experiences from {filepath}")
                return jsonify({"respuesta": respuesta})
            
            except Exception as e:
                logger.error(f"Error importing experience: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({"respuesta": f"❌ Error al importar: {str(e)}"})

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

REGLA CRÍTICA - CUÁNDO OMITIR SALUDOS:
❌ NO uses saludos como "¡Hola!", "¡Buenas!", "¿Qué tal?" cuando:
   - El usuario hace una pregunta técnica específica
   - El usuario solicita análisis de archivos/código
   - El usuario pide corrección de errores
   - La conversación ya está en curso (no es el primer mensaje)
   
✅ SÍ usa saludos cuando:
   - Es el primer mensaje de la conversación
   - El usuario te saluda directamente
   - Hay una pausa larga en la conversación

CÓMO RESPONDER SEGÚN EL CONTEXTO:

1. SALUDOS DIRECTOS ("hola", "buenas", etc.):
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

4. SOLICITUDES TÉCNICAS ("analiza", "corrige", "explica", "busca errores"):
   - ⚠️ IMPORTANTE: NO incluyas saludo inicial
   - Ve directo al grano con la respuesta técnica
   - Sé conciso y preciso
   - Ejemplo CORRECTO: "El archivo manifest.json define la configuración de tu PWA..."
   - Ejemplo INCORRECTO: "¡Hola! El archivo manifest.json..."

5. SOLICITUDES DE CÓDIGO ("dame código", "muéstrame el código", "escribe código"):
   - CONFIRMA qué tipo de código necesita
   - Pide detalles específicos del requerimiento
   - Una vez claro, genera el código usando el backend
   - Presenta el código de forma clara

REGLAS CRÍTICAS:
- NUNCA uses la misma frase dos veces
- NUNCA listes comandos (/setpath, /create, etc.) a menos que te lo pidan explícitamente
- Mantén respuestas de 2-4 oraciones (excepto respuestas técnicas que pueden ser más largas)
- Termina con una pregunta o invitación a continuar (solo en conversaciones, no en respuestas técnicas)
- Sé específico, no genérico
- ⚠️ EN RESPUESTAS TÉCNICAS: Omite saludos, ve directo al contenido"""

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
                        codigo_generado = generar_codigo(requerimiento, max_intentos=3)  # Aumentar a 3 intentos
                        
                        print(f"🔍 DEBUG - Código generado: {len(codigo_generado) if codigo_generado else 0} chars")
                        
                        if codigo_generado and len(codigo_generado) > 20:
                            # La validación ya se hizo en generar_codigo() con _es_codigo_de_calidad()
                            print(f"✅ Código generado y validado correctamente")
                            respuesta_ia = f"```python\n{codigo_generado}\n```"
                        else:
                            print(f"❌ Código NO generado o muy corto")
                            respuesta_ia = "No pude generar código válido después de varios intentos. ¿Puedes ser más específico?"
                        
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

        # =========================
        # CODE_FIX - Fix automático de código
        # =========================
        elif intencion == "code_fix":
            mensaje_usuario = contexto.get("mensaje", "")
            return self.fix_code(mensaje_usuario)


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

    def fix_code(self, message: str):
        """Fix code - versión mínima temporal"""
        from agent.llm.client import generate as generate_llm
        
        prompt = f"""
Fix this Dart code.

RULES:
- Return ONLY code
- Do not use markdown
- Preserve original structure
- Preserve original strings
- Fix only syntax/errors

CODE:
{message}
"""

        print("\n=== FIX PROMPT START ===\n")
        print(prompt)
        print("\n=== FIX PROMPT END ===\n")

        response = generate_llm(prompt, max_tokens=2000, use_case="fix")
        
        print("\n=== FIX RESPONSE START ===\n")
        print(response[:500] if response else "EMPTY")
        print("\n=== FIX RESPONSE END ===\n")

        return jsonify({"respuesta": response})
