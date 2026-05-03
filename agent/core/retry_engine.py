"""
Motor de reintentos robusto con estrategias fallback.

Niveles de agresión:
1. CONSERVATIVE: Prompt estricto, pocos tokens
2. SMART (default): Balance entre calidad y velocidad
3. AGGRESSIVE: Prompt corto y directo, máx tokens
4. HEURISTIC: Fixes locales (regex, patterns)
5. EMERGENCY: Copia original con comentarios
"""

from typing import Callable, Dict, Any, Optional
from agent.llm.client import generate
from agent.extractor import extraer_codigo

class RetryEngine:
    def __init__(self):
        self.strategies = {
            "conservative": self._conservative,
            "smart": self._smart,
            "aggressive": self._aggressive,
            "heuristic": self._heuristic,
            "emergency": self._emergency,
        }

    def ejecutar(
        self,
        codigo: str,
        objetivo: str,  # "fix", "enhance", "create"
        estrategia: str = "smart",
        max_tokens: int = 1200,
    ) -> Optional[str]:
        """
        Ejecuta reintentos progresivos hasta conseguir resultado válido.
        
        Args:
            codigo: Código a procesar
            objetivo: "fix" (reparar), "enhance" (mejorar), "create" (generar)
            estrategia: Nivel inicial de agresión
            max_tokens: Máximo de tokens del modelo
        
        Returns:
            Código generado o None si falla todo
        """

        # Intenta estrategia inicial
        resultado = self.strategies[estrategia](codigo, objetivo, max_tokens)
        if self._es_valido(resultado):
            return resultado

        # Fallback progresivo
        orden_fallback = ["smart", "aggressive", "heuristic", "emergency"]
        for fallback_strat in orden_fallback:
            if fallback_strat == estrategia:
                continue
            resultado = self.strategies[fallback_strat](codigo, objetivo, max_tokens)
            if self._es_valido(resultado):
                return resultado

        return None

    def _conservative(self, codigo: str, objetivo: str, max_tokens: int) -> Optional[str]:
        """Prompt muy estructurado, pocos tokens"""
        prompt = f"""SOLO código. Sin explicaciones.

OBJETIVO: {objetivo}

```python
{codigo[:1000]}
```

RESULTADO:"""
        resp = generate(prompt, max_tokens=min(max_tokens, 500))
        return extraer_codigo(resp) if resp else None

    def _smart(self, codigo: str, objetivo: str, max_tokens: int) -> Optional[str]:
        """Balance: explícito pero flexible"""
        prompt = f"""Eres experto en Python.

TAREA: {objetivo}

Devuelve SOLO código válido. Sin charla.

{codigo[:1500]}
"""
        resp = generate(prompt, max_tokens=max_tokens)
        return extraer_codigo(resp) if resp else None

    def _aggressive(self, codigo: str, objetivo: str, max_tokens: int) -> Optional[str]:
        """Prompt corto y directo"""
        objetivo_map = {
            "fix": "Corrige todo",
            "enhance": "Mejora este código",
            "create": "Completa este código"
        }

        prompt = f"{objetivo_map.get(objetivo, objetivo)}:\n\n{codigo[:2000]}"
        resp = generate(prompt, max_tokens=max_tokens)
        return extraer_codigo(resp) if resp else None

    def _heuristic(self, codigo: str, objetivo: str, max_tokens: int) -> Optional[str]:
        """Fixes locales sin LLM"""
        import re

        nuevos = codigo

        # Fix 1: Imports faltantes
        if "pd." in nuevos and "import pandas" not in nuevos:
            nuevos = "import pandas as pd\n" + nuevos

        # Fix 2: Variables indefinidas simples
        if "np." in nuevos and "import numpy" not in nuevos:
            nuevos = "import numpy as np\n" + nuevos

        # Fix 3: Indentación
        lineas = nuevos.split("\n")
        try:
            nuevos = "\n".join(lineas)
        except:
            pass

        # Fix 4: Sintaxis común
        nuevos = re.sub(r"print\s*\(([^)]+)\)", r"print(\1)", nuevos)

        return nuevos if nuevos != codigo else None

    def _emergency(self, codigo: str, objetivo: str, max_tokens: int) -> Optional[str]:
        """Fallback extremo: retorna original con warning"""
        return f"""# ⚠️ EMERGENCY MODE - Original code returned
# Attempted: {objetivo}

{codigo}
"""

    def _es_valido(self, resultado: Optional[str]) -> bool:
        """Valida que el resultado sea código útil"""
        if not resultado:
            return False

        # No es chatbot
        basura = ["i explain", "this code", "sorry", "cannot"]
        if any(b in resultado.lower() for b in basura):
            return False

        # Tiene contenido
        if len(resultado.strip()) < 20:
            return False

        return True
