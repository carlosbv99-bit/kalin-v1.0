"""
Estrategia para procesar archivos Python.
Especializada en: reparación, testing, optimización.
"""

from typing import Optional
from agent.actions.strategies.base_strategy import BaseStrategy
from agent.analyzer import analizar_codigo


class PythonStrategy(BaseStrategy):
    """Estrategia especializada en código Python"""

    def analizar(self, codigo: str) -> str:
        """Analiza código Python"""
        # Reutiliza analyzer existente
        return analizar_codigo(codigo)

    def reparar(self, codigo: str, analisis: str) -> Optional[str]:
        """
        Repara Python usando retry progresivo.
        Si LLM falla, usa heurísticas locales.
        """

        # Construye prompt especializado para Python
        prompt = f"""Eres experto en Python profesional.

PROBLEMAS ENCONTRADOS:
{analisis}

Corrige COMPLETAMENTE el código. Sin explicaciones.

```python
{codigo[:2000]}
```

CÓDIGO CORREGIDO:"""

        # Usa retry engine con estrategia smart
        resultado = self.retry_engine.ejecutar(
            codigo=codigo,
            objetivo="fix",
            estrategia="smart",
            max_tokens=1500,
        )

        return resultado

    def mejorar(self, codigo: str) -> Optional[str]:
        """
        Mejora código: optimización, claridad, testing.
        """

        prompt = f"""Mejora este código Python:

1. Hazlo más Pythónico
2. Añade type hints si faltan
3. Optimiza performance
4. Añade docstrings si faltan

```python
{codigo[:2000]}
```

CÓDIGO MEJORADO:"""

        resultado = self.retry_engine.ejecutar(
            codigo=codigo,
            objetivo="enhance",
            estrategia="smart",
            max_tokens=1500,
        )

        return resultado

    def validar(self, codigo: str) -> bool:
        """Valida sintaxis Python básica"""
        try:
            compile(codigo, '<string>', 'exec')
            return True
        except SyntaxError:
            return False
