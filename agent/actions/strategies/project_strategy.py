"""
Estrategia para diseñar/mejorar proyectos completos.
Entiende contexto: dependencias, estructura, requisitos.
"""

from typing import Optional, Dict, List
from agent.actions.strategies.base_strategy import BaseStrategy
from agent.core.project_analyzer import ProjectAnalyzer


class ProjectStrategy(BaseStrategy):
    """Estrategia para proyectos multi-archivo"""

    def __init__(self, retry_engine, ruta_proyecto: str):
        super().__init__(retry_engine)
        self.analyzer = ProjectAnalyzer(ruta_proyecto)
        self.proyecto_info = self.analyzer.get_resumen()

    def analizar(self, codigo: str) -> str:
        """Analiza proyecto completo"""
        resumen = self.analyzer.get_resumen()

        analisis = f"""
ANÁLISIS DEL PROYECTO
====================

Tipo: {resumen['tipo_principal']}
Total archivos: {resumen['total_archivos']}
Tipos encontrados: {resumen['tipos']}

Archivos principales:
{chr(10).join('- ' + f for f in resumen['archivos'][:10])}

CONTEXTO PARA LA REPARACIÓN:
"""
        return analisis

    def reparar(self, codigo: str, analisis: str) -> Optional[str]:
        """
        Repara proyecto considerando contexto completo.
        """

        # Detecta qué tipo de archivo es
        tipo_detectado = self._detectar_tipo_archivo(codigo)

        prompt = f"""{analisis}

TAREA: Diseña la estructura y código completo para mejorar este proyecto.

Considera:
1. Arquitectura escalable
2. Separación de responsabilidades
3. Testing
4. Documentación

RESPONDE CON:
- Estructura de directorios (como árbol)
- Archivos principales con código
- Cambios clave

{codigo[:1000]}
"""

        resultado = self.retry_engine.ejecutar(
            codigo=codigo,
            objetivo="create",
            estrategia="aggressive",  # Proyectos nuevos: más agresivo
            max_tokens=2000,
        )

        return resultado

    def mejorar(self, codigo: str) -> Optional[str]:
        """Mejora todo el proyecto"""
        return self.reparar(codigo, self.analizar(codigo))

    def _detectar_tipo_archivo(self, codigo: str) -> str:
        """Detecta qué tipo de archivo es por su contenido"""
        contenido = codigo[:500].lower()

        if "flutter" in contenido or "dartwidget" in contenido:
            return "flutter"
        if "import flask" in contenido or "@app.route" in contenido:
            return "flask"
        if "import django" in contenido or "from django" in contenido:
            return "django"
        if "def " in contenido and ("class " in contenido or "import " in contenido):
            return "python_project"

        return "unknown"

    def get_contexto_proyecto(self) -> Dict:
        """Retorna contexto para usar en prompts"""
        imports = self.analyzer.get_imports_proyecto()
        
        return {
            "tipo": self.proyecto_info["tipo_principal"],
            "total_archivos": self.proyecto_info["total_archivos"],
            "tipos": self.proyecto_info["tipos"],
            "imports_detectados": list(imports)[:10],
            "resumen": self.proyecto_info,
        }
