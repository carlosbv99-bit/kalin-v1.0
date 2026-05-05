"""
Strategies: módulo con estrategias especializadas por tipo de código.
"""

from agent.actions.strategies.base_strategy import BaseStrategy
from agent.actions.strategies.python_strategy import PythonStrategy
from agent.actions.strategies.project_strategy import ProjectStrategy

__all__ = ["BaseStrategy", "PythonStrategy", "ProjectStrategy"]
