from fastapi import FastAPI, Request
import requests
import os
import uvicorn
from pydantic import BaseModel
from chatbot import ask_question

# Configurar FastAPI
app = FastAPI()

# Modelo de datos para recibir preguntas
class Question(BaseModel):
    question: str
    
##port = int(os.environ.get("PORT", 10000))

##if __name__ == "__main__":
  ##  uvicorn.run(app, host="0.0.0.0", port=port)

# Endpoint del chatbot
@app.post("/chat/")
async def chat(question: Question):
    respuesta = ask_question(question.question)
    return {"response": respuesta}

##IS AVAILABLE
@app.get("/health")
async def health_check():
    return {"status": "ok"}

