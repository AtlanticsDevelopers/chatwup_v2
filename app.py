from fastapi import FastAPI, Request
import requests
import os
from pydantic import BaseModel
from chatbot import ask_question

# Configurar FastAPI
app = FastAPI()

# Modelo de datos para recibir preguntas
class Question(BaseModel):
    question: str

# Endpoint del chatbot
@app.post("/chat/")
async def chat(question: Question):
    respuesta = ask_question(question.question)
    return {"response": respuesta}


@app.post("/webhook/")
async def handle_whatsapp_message(request: Request):
    data = await request.json()
    print("📩 Mensaje recibido de WhatsApp:", json.dumps(data, indent=2))  # Debugging en logs de Render

    if "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                message_data = change.get("value", {}).get("messages", [])
                for message in message_data:
                    sender_id = message["from"]
                    user_message = message["text"]["body"]

                    print(f"📥 Mensaje recibido: {user_message} de {sender_id}")

                    # 🔹 Llamar al chatbot
                    bot_response = requests.post(CHATBOT_API_URL, json={"question": user_message})
                    bot_reply_text = bot_response.json().get("response", "Lo siento, no pude procesar eso.")

                    # 🔹 Enviar respuesta a WhatsApp
                    send_whatsapp_message(sender_id, bot_reply_text)

    return {"status": "received"}