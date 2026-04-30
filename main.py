from fastapi import FastAPI
from pydantic import BaseModel
from agent import app

api = FastAPI()

class Request(BaseModel):
    prompt: str

@api.post("/ask")
def ask(req: Request):
    result = app.invoke({"input": req.prompt})
    return {"response": result["output"]}