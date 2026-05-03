"""
Estrategias base para procesar código según su tipo.
Patrón Strategy: cada tipo de código tiene su propia lógica.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from agent.core.retry_engine import RetryEngine
from agent.analyzer import analizar_codigo


class BaseStrategy(ABC):
    """Clase base para todas las estrategias"""

    def __init__(self, retry_engine: RetryEngine):
        self.retry_engine = retry_engine
        self.nombre = self.__class__.__name__

    @abstractmethod
    def analizar(self, codigo: str) -> str:
        """Analiza el código y retorna problemas encontrados"""
        pass

    @abstractmethod
    def reparar(self, codigo: str, analisis: str) -> Optional[str]:
        """Repara el código basado en el análisis"""
        pass

    @abstractmethod
    def mejorar(self, codigo: str) -> Optional[str]:
        """Mejora el código sin necesidad de análisis"""
        pass

    def ejecutar(self, codigo: str, accion: str = "fix") -> Optional[str]:
        """Pipeline completo: analiza -> repara/mejora"""
        if accion == "analyze":
            return self.analizar(codigo)

        analisis = self.analizar(codigo)
        
        if accion == "fix":
            return self.reparar(codigo, analisis)
        elif accion == "enhance":
            return self.mejorar(codigo)

        return None
