from flask import jsonify
import os
from agent.analyzer import analizar_codigo
from agent.actions.tools.fix_tool import generar_codigo, reparar_codigo
from agent.llm.client import is_available, get_provider_status
from agent.core.state_manager import StateManager
from agent.core.retry_engine import RetryEngine
from agent.core.project_analyzer import ProjectAnalyzer
from agent.actions.strategies import PythonStrategy, ProjectStrategy

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
                return jsonify({"respuesta": "❌ Usa: /setpath ruta"})
            if not self.state_manager.set_ruta(ruta):
                return jsonify({"respuesta": f"❌ Ruta no válida: {ruta}"})
            
            # Reinitialize project analyzer
            self.project_analyzer = ProjectAnalyzer(ruta)
            self._strategies_cache = {}
            
            return jsonify({"respuesta": f"📂 Ruta configurada: {ruta}"})

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

            codigo = utils["leer_archivo"](ruta)
            if not codigo:
                return jsonify({"respuesta": "❌ No se pudo leer el archivo"})

            # Registra último archivo
            self.state_manager.set_ultimo_archivo(ruta, codigo)

            # Selecciona estrategia según tipo
            tipo_archivo = self._detectar_tipo_archivo(ruta)
            
            if tipo_archivo == "python":
                estrategia = self._get_strategy("python")
                nuevo = estrategia.reparar(codigo, estrategia.analizar(codigo))
            else:
                # Fallback a código existente si no es Python
                analisis = analizar_codigo(codigo)
                nuevo = reparar_codigo(codigo, analisis)

            if not nuevo:
                self.state_manager.registrar_fallo()
                status = get_provider_status()
                return jsonify({
                    "respuesta": "❌ No se pudo generar código. Verifica el proveedor LLM configurado y el estado del servidor.",
                    "preview": "",
                    "status": status
                })

            # Detecta si es diff o código completo
            es_diff = nuevo.strip().startswith("---") or nuevo.strip().startswith("@@")
            
            if es_diff:
                # Es diff: aplica internamente y obtén código nuevo
                print(f"📋 Diff detectado, aplicando...")
                # TODO: implementar aplicar_diff correctamente
                # Por ahora: usa el diff tal cual para preview
                nuevo_limpio = nuevo
                diff = nuevo
                valido = True
            else:
                # Es código: limpia, valida, genera diff
                nuevo_limpio = utils["limpiar_codigo"](nuevo) or nuevo
                valido = utils["es_codigo_valido"](nuevo_limpio)
                diff = utils["generar_diff"](codigo, nuevo_limpio)

            self.state_manager.set_ultimo_fix(ruta, codigo, nuevo_limpio)
            return jsonify({
                "respuesta": "⚠️ Modo seguro activo (usa /apply)",
                "preview": nuevo_limpio[:800],
                "diff": diff,
                "valido": valido
            })

        if intencion == "analyze":
            nombre = args.get("arg")
            if not ruta_proyecto:
                return jsonify({"respuesta": "⚠️ Primero usa /setpath"})
            if not nombre:
                return jsonify({"respuesta": "❌ Usa: /analyze archivo"})
            if not is_available():
                status = get_provider_status()
                return jsonify({
                    "respuesta": "❌ No hay proveedor LLM disponible. Revisa Ollama local o configura OPENAI_API_KEY/ANTHROPIC_API_KEY.",
                    "status": status
                })

            ruta = utils["buscar_archivo_inteligente"](nombre, ruta_proyecto)
            if not ruta:
                return jsonify({"respuesta": "❌ Archivo no encontrado"})

            codigo = utils["leer_archivo"](ruta)
            if not codigo:
                return jsonify({"respuesta": "❌ No se pudo leer el archivo"})

            analisis = analizar_codigo(codigo)
            return jsonify({"respuesta": "🔍 Análisis completado", "analysis": analisis})

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

            codigo = utils["leer_archivo"](ruta)
            if not codigo:
                return jsonify({"respuesta": "❌ No se pudo leer el archivo"})

            analisis = analizar_codigo(codigo)
            nuevo = reparar_codigo(codigo, analisis)
            if not nuevo:
                return jsonify({"respuesta": "❌ No se pudo refactorizar el código. Verifica el proveedor LLM configurado y el estado del servidor.", "preview": ""})

            diff = utils["generar_diff"](codigo, nuevo)
            return jsonify({
                "respuesta": "✅ Refactorización propuesta",
                "preview": nuevo[:800],
                "diff": diff,
                "valido": utils["es_codigo_valido"](nuevo)
            })

        if intencion == "help":
            return jsonify({
                "respuesta": "Comandos disponibles: /setpath <ruta>, /scan, /fix <archivo>, /apply, /analyze <archivo>, /create <requerimiento>, /refactor <archivo>"
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
