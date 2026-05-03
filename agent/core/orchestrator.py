from agent.core.brain import construir_contexto, planificar
from agent.actions.executor import Executor

class Orchestrator:
    def __init__(self):
        self.executor = Executor()

    def handle(self, mensaje, estado, utils):
        # 1. construir contexto
        contexto = construir_contexto(mensaje, estado)

        # 2. planificar
        contexto = planificar(contexto)

        # 3. ejecutar
        return self.executor.ejecutar(contexto, utils)