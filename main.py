from fastapi import FastAPI
from pydantic import BaseModel

from agent.llm_client import generar_respuesta  # 👈 cambia esto

api = FastAPI()

class Request(BaseModel):
    prompt: str

@api.post("/ask")
def ask(req: Request):
    try:
        result = generar_respuesta(req.prompt)

        return {
            "response": result
        }

    except Exception as e:
        return {
            "error": str(e)
        }