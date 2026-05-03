"""
Analizador de proyectos: mapea estructura, dependencias y tipos.
Permite al agente entender el contexto completo.
"""

import os
from typing import Dict, List, Set, Optional
from pathlib import Path


        class ProjectAnalyzer:
    def __init__(self, ruta_proyecto: str):
        self.ruta = os.path.abspath(ruta_proyecto)
        self.archivos: Dict[str, Dict] = {}  # ruta -> {tipo, size, ruta_absoluta}
        self._escanear()

    def _escanear(self):
        """Mapea todos los archivos del proyecto"""
        for root, dirs, files in os.walk(self.ruta):
            # Ignora directorios comunes
            dirs[:] = [
                d for d in dirs
                if d not in [".git", "node_modules", "__pycache__", ".gradle", "build"]
            ]

            for file in files:
                ruta_completa = os.path.join(root, file)
                relativa = os.path.relpath(ruta_completa, self.ruta)

                tipo = self._detectar_tipo(file)
                if tipo:
                    self.archivos[relativa] = {
                        "tipo": tipo,
                        "size": os.path.getsize(ruta_completa),
                        "ruta_absoluta": ruta_completa,
                    }

    def _detectar_tipo(self, nombre: str) -> Optional[str]:
        """Clasifica el tipo de archivo"""
        ext = os.path.splitext(nombre)[1].lower()

        tipos = {
            ".py": "python",
            ".dart": "flutter",
            ".kt": "kotlin",
            ".java": "java",
            ".js": "javascript",
            ".ts": "javascript",
            ".jsx": "react",
            ".tsx": "react",
            ".html": "html",
            ".gradle": "gradle",
            ".kts": "gradle-kotlin",
        }

        tipo = tipos.get(ext)

        # 🔍 DEBUG (clave ahora mismo)
        print(f"[SCAN] archivo={nombre} ext={ext} tipo={tipo}")

        return tipo

    def get_archivos_por_tipo(self, tipo: str) -> List[str]:
        """Retorna lista de archivos de un tipo"""
        return [r for r, d in self.archivos.items() if d["tipo"] == tipo]

    def get_tipo_proyecto(self) -> str:
        """Detecta el tipo principal de proyecto"""
        tipos_encontrados = {}

        for data in self.archivos.values():
            t = data["tipo"]
            tipos_encontrados[t] = tipos_encontrados.get(t, 0) + 1

        if not tipos_encontrados:
            return "unknown"

        return max(tipos_encontrados, key=tipos_encontrados.get)

    def get_resumen(self) -> Dict:
        """Retorna resumen del proyecto"""
        tipos_encontrados = {}

        for data in self.archivos.values():
            t = data["tipo"]
            tipos_encontrados[t] = tipos_encontrados.get(t, 0) + 1

        return {
            "ruta": self.ruta,
            "tipo_principal": self.get_tipo_proyecto(),
            "total_archivos": len(self.archivos),
            "tipos": tipos_encontrados,
            "archivos": list(self.archivos.keys())[:20],
        }

    def buscar_archivo(self, nombre: str, tipo_hint: Optional[str] = None) -> Optional[str]:
        """Busca un archivo por nombre, opcionalmente filtrado por tipo"""
        nombre_lower = nombre.lower()

        for ruta, data in self.archivos.items():
            if tipo_hint and data["tipo"] != tipo_hint:
                continue

            if (
                ruta.lower().endswith(nombre_lower)
                or os.path.basename(ruta).lower() == nombre_lower
            ):
                return ruta

        return None

    def get_imports_proyecto(self) -> Set[str]:
        """Extrae todos los imports del proyecto (Python)"""
        imports = set()
        archivos_py = self.get_archivos_por_tipo("python")

        for archivo in archivos_py[:10]:  # límite para no bloquear
            ruta_abs = self.archivos[archivo]["ruta_absoluta"]

            try:
                with open(ruta_abs, "r", encoding="utf-8", errors="ignore") as f:
                    for linea in f:
                        linea = linea.strip()
                        if linea.startswith("import ") or linea.startswith("from "):
                            imports.add(linea)
            except:
                pass

        return imports