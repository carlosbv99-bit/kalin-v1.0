from fastapi import FastAPI
from pydantic import BaseModel

from agent.llm.client import generate

api = FastAPI()

class Request(BaseModel):
    prompt: str

@api.post("/ask")
def ask(req: Request):
    try:
        result = generate(req.prompt)
        return {
            "response": result
        }
    except Exception as e:
        return {
            "error": str(e)
        }