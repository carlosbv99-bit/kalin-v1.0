# agent/core/prompt_builder.py
"""
Sistema de Prompts Dinámicos para Kalin

Construye prompts contextualizados basados en:
- Intención del usuario
- Contexto conversacional
- Tipo de proyecto detectado
- Archivos disponibles
- Historial de la conversación
"""

from typing import Dict, Any, Optional, List


class PromptBuilder:
    """Constructor de prompts dinámicos y contextuales"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Carga plantillas base para diferentes intenciones"""
        return {
            "analyze": self._template_analyze(),
            "fix": self._template_fix(),
            "create": self._template_create(),
            "scan": self._template_scan(),
            "refactor": self._template_refactor(),
        }
    
    def build_prompt(
        self,
        intention: str,
        user_message: str,
        context: Dict[str, Any],
        code_content: Optional[str] = None,
        project_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Construye un prompt dinámico basado en el contexto
        
        Args:
            intention: Intención detectada (analyze, fix, create, etc.)
            user_message: Mensaje original del usuario
            context: Contexto adicional (tipo de proyecto, archivos, etc.)
            code_content: Código a analizar/corregir (opcional)
            project_info: Información del proyecto (opcional)
        
        Returns:
            Prompt estructurado y contextualizado
        """
        template = self.templates.get(intention)
        if not template:
            # Fallback: usar template genérico
            template = self._template_generic()
        
        # Detectar tipo de proyecto automáticamente
        project_type = self._detect_project_type(context, code_content)
        
        # Construir secciones del prompt
        sections = {
            "role": self._get_role_for_intention(intention, project_type),
            "user_intent": user_message,
            "context": self._format_context(context, project_type),
            "project_info": self._format_project_info(project_info) if project_info else "",
            "code_section": self._format_code_section(code_content) if code_content else "",
            "task": self._get_task_description(intention, project_type),
            "output_format": self._get_output_format(intention),
        }
        
        # Renderizar template con secciones
        prompt = template.format(**sections)
        
        return prompt
    
    def _detect_project_type(self, context: Dict, code_content: Optional[str] = None) -> str:
        """Detecta automáticamente el tipo de proyecto"""
        # Por contexto explícito
        if context.get("project_type"):
            return context["project_type"]
        
        # Por archivos mencionados
        files = context.get("files", [])
        for file in files:
            if "pubspec.yaml" in file or ".dart" in file:
                return "flutter"
            elif "build.gradle" in file or ".kt" in file or ".java" in file:
                return "android_native"
            elif ".py" in file:
                return "python"
            elif "package.json" in file or ".js" in file or ".ts" in file:
                return "javascript"
        
        # Por contenido del código
        if code_content:
            if "import 'package:flutter'" in code_content:
                return "flutter"
            elif "def " in code_content and "import" in code_content:
                return "python"
            elif "public class" in code_content or "import android" in code_content:
                return "android_native"
        
        return "unknown"
    
    def _get_role_for_intention(self, intention: str, project_type: str) -> str:
        """Define el rol del LLM según la intención y tipo de proyecto"""
        roles = {
            "flutter": {
                "analyze": "Eres un experto senior en Flutter/Dart con 10 años de experiencia en desarrollo móvil.",
                "fix": "Eres un especialista en debugging de Flutter/Dart, experto en encontrar y corregir errores.",
                "create": "Eres un arquitecto de software Flutter, especializado en crear código limpio y escalable.",
                "scan": "Eres un auditor de proyectos Flutter, experto en análisis de arquitectura y mejores prácticas.",
                "refactor": "Eres un experto en refactorización de código Flutter, enfocado en clean code y performance.",
            },
            "android_native": {
                "analyze": "Eres un experto senior en Android nativo (Java/Kotlin) con amplia experiencia.",
                "fix": "Eres un especialista en debugging de Android nativo, experto en resolver problemas complejos.",
                "create": "Eres un arquitecto de software Android, especializado en patrones modernos (MVVM, Clean Architecture).",
                "scan": "Eres un auditor de proyectos Android, experto en análisis de calidad y arquitectura.",
                "refactor": "Eres un experto en refactorización de código Android, enfocado en Kotlin idiomatic y performance.",
            },
            "python": {
                "analyze": "Eres un experto senior en Python con experiencia en múltiples frameworks y paradigmas.",
                "fix": "Eres un especialista en debugging de Python, experto en encontrar bugs sutiles.",
                "create": "Eres un arquitecto de software Python, especializado en código pythonic y eficiente.",
                "scan": "Eres un auditor de proyectos Python, experto en PEP 8, arquitectura y mejores prácticas.",
                "refactor": "Eres un experto en refactorización de Python, enfocado en código limpio y mantenible.",
            },
            "javascript": {
                "analyze": "Eres un experto senior en JavaScript/TypeScript con experiencia en frontend y backend.",
                "fix": "Eres un especialista en debugging de JavaScript, experto en resolver problemas asíncronos.",
                "create": "Eres un arquitecto de software JavaScript, especializado en patrones modernos y clean code.",
                "scan": "Eres un auditor de proyectos JavaScript, experto en calidad de código y arquitectura.",
                "refactor": "Eres un experto en refactorización de JavaScript/TypeScript, enfocado en código moderno.",
            },
        }
        
        project_roles = roles.get(project_type, roles["python"])
        return project_roles.get(intention, "Eres un experto desarrollador de software.")
    
    def _get_task_description(self, intention: str, project_type: str) -> str:
        """Describe la tarea específica según intención y tipo de proyecto"""
        tasks = {
            "analyze": {
                "flutter": """
TAREA: Analiza el código Flutter proporcionado y proporciona:
1. Descripción clara de qué hace el código
2. Posibles problemas o áreas de mejora
3. Sugerencias específicas para optimización
4. Evaluación de adherence a Material Design y mejores prácticas Flutter""",
                "android_native": """
TAREA: Analiza el código Android proporcionado y proporciona:
1. Descripción clara de la funcionalidad
2. Posibles memory leaks o problemas de performance
3. Sugerencias de modernización (Kotlin coroutines, Jetpack, etc.)
4. Evaluación de arquitectura (MVVM, Clean Architecture)""",
                "python": """
TAREA: Analiza el código Python proporcionado y proporciona:
1. Descripción clara de la funcionalidad
2. Problemas potenciales (bugs, edge cases)
3. Sugerencias de optimización y pythonic code
4. Evaluación de PEP 8 y buenas prácticas""",
            },
            "fix": {
                "flutter": """
TAREA: Identifica y corrige TODOS los errores en el código Flutter:
1. Errores de compilación
2. Bugs lógicos
3. Problemas de UI/UX
4. Memory leaks o performance issues
5. Violaciones de mejores prácticas

Proporciona el código CORREGIDO completo.""",
                "android_native": """
TAREA: Identifica y corrige TODOS los errores en el código Android:
1. Errores de compilación
2. Crashes potenciales (NullPointerException, etc.)
3. Memory leaks
4. Problemas de threading
5. Violaciones de arquitectura

Proporciona el código CORREGIDO completo.""",
            },
            "create": {
                "flutter": """
TAREA: Genera código Flutter profesional basado en el requerimiento del usuario:
- Usa Material 3 design
- Implementa state management apropiado
- Sigue principios SOLID
- Código limpio y bien documentado
- Manejo de errores robusto""",
            },
            "scan": {
                "flutter": """
TAREA: Realiza un análisis COMPLETO del proyecto Flutter:
1. Estructura de carpetas y organización
2. Dependencias y versiones
3. Arquitectura general
4. Áreas críticas que necesitan atención
5. Recomendaciones prioritarias""",
            },
        }
        
        intention_tasks = tasks.get(intention, {})
        return intention_tasks.get(project_type, f"TAREA: Ejecuta la acción '{intention}' sobre el código proporcionado.")
    
    def _get_output_format(self, intention: str) -> str:
        """Define el formato de salida esperado"""
        formats = {
            "analyze": """
FORMATO DE RESPUESTA:
- Usa lenguaje claro y técnico pero accesible
- Organiza en secciones con emojis para mejor legibilidad
- Prioriza los problemas más críticos primero
- Sé específico con ejemplos cuando sea posible""",
            "fix": """
FORMATO DE RESPUESTA:
- Lista los errores encontrados (priorizados por severidad)
- Proporciona el código CORREGIDO completo entre marcadores --- CODIGO CORREGIDO ---
- Explica brevemente cada corrección importante
- No incluyas texto introductorio antes del código""",
            "create": """
FORMATO DE RESPUESTA:
- Proporciona SOLO el código generado
- Sin explicaciones extensas a menos que se soliciten
- Código listo para copiar y pegar
- Incluye imports necesarios""",
            "scan": """
FORMATO DE RESPUESTA:
- Resumen ejecutivo al inicio
- Análisis detallado por categorías
- Recomendaciones priorizadas (alta/media/baja)
- Métricas cuantitativas cuando sea posible""",
        }
        
        return formats.get(intention, "FORMATO: Responde de manera clara y estructurada.")
    
    def _format_context(self, context: Dict, project_type: str) -> str:
        """Formatea el contexto adicional"""
        if not context:
            return ""
        
        lines = ["CONTEXTO ADICIONAL:"]
        
        if context.get("conversation_history"):
            lines.append(f"- Historial: Usuario está trabajando en una sesión activa")
        
        if context.get("previous_errors"):
            lines.append(f"- Errores previos detectados: {len(context['previous_errors'])}")
        
        if context.get("user_level"):
            lines.append(f"- Nivel del usuario: {context['user_level']}")
        
        if project_type != "unknown":
            lines.append(f"- Tipo de proyecto detectado: {project_type.upper()}")
        
        return "\n".join(lines) if len(lines) > 1 else ""
    
    def _format_project_info(self, project_info: Dict) -> str:
        """Formatea información del proyecto"""
        if not project_info:
            return ""
        
        lines = ["INFORMACIÓN DEL PROYECTO:"]
        
        if project_info.get("ruta"):
            lines.append(f"- Ruta: {project_info['ruta']}")
        
        if project_info.get("total_archivos"):
            lines.append(f"- Total archivos: {project_info['total_archivos']}")
        
        if project_info.get("tipos"):
            lines.append(f"- Tipos de archivo:")
            for tipo, cantidad in project_info['tipos'].items():
                lines.append(f"  • {tipo}: {cantidad}")
        
        return "\n".join(lines)
    
    def _format_code_section(self, code_content: str) -> str:
        """Formatea la sección de código"""
        return f"""
CÓDIGO A ANALIZAR:
```
{code_content}
```
"""
    
    # ==================== TEMPLATES BASE ====================
    
    def _template_analyze(self) -> str:
        return """{role}

MENSAJE DEL USUARIO: "{user_intent}"

{context}

{project_info}

{code_section}

{task}

{output_format}

IMPORTANTE:
- Adapta tu respuesta al nivel técnico implícito en la pregunta del usuario
- Si el usuario parece principiante, explica conceptos técnicos de forma simple
- Si el usuario es avanzado, sé conciso y técnico
- Sé útil y práctico, no solo teórico"""
    
    def _template_fix(self) -> str:
        return """{role}

MENSAJE DEL USUARIO: "{user_intent}"

{context}

{code_section}

{task}

{output_format}

REGLAS CRÍTICAS:
1. NO modifiques la lógica funcional del código sin razón
2. Preserva todos los imports y dependencias
3. Mantén el estilo de código existente
4. Si hay múltiples soluciones, elige la más simple
5. El código debe ser production-ready"""
    
    def _template_create(self) -> str:
        return """{role}

REQUERIMIENTO DEL USUARIO: "{user_intent}"

{context}

{task}

{output_format}

REGLAS:
1. Genera código completo y funcional
2. Incluye manejo de errores básico
3. Sigue las convenciones del lenguaje/framework
4. Código limpio y legible
5. Comentarios solo donde sean necesarios"""
    
    def _template_scan(self) -> str:
        return """{role}

MENSAJE DEL USUARIO: "{user_intent}"

{context}

{project_info}

{task}

{output_format}

ENFOQUE:
- Sé exhaustivo pero conciso
- Prioriza problemas críticos
- Proporciona acciones concretas
- Balancea crítica constructiva con reconocimiento de aciertos"""
    
    def _template_refactor(self) -> str:
        return """{role}

MENSAJE DEL USUARIO: "{user_intent}"

{context}

{code_section}

TAREA: Refactoriza el código para mejorar:
1. Legibilidad y mantenibilidad
2. Performance (si aplica)
3. Adherencia a principios SOLID/Clean Code
4. Eliminación de code smells
5. Mejora de estructura sin cambiar funcionalidad

{output_format}

REGLAS:
- NO cambies el comportamiento funcional
- Preserva la API pública
- Documenta cambios significativos
- Justifica cada refactorización importante"""
    
    def _template_generic(self) -> str:
        return """Eres un asistente experto en desarrollo de software.

MENSAJE DEL USUARIO: "{user_intent}"

{context}

{code_section}

TAREA: Responde de manera útil y técnica al requerimiento del usuario.

FORMATO: Sé claro, estructurado y práctico."""
