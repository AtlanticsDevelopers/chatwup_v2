from fastapi import FastAPI
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

'''
from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

# 🔹 Credenciales de la API de Meta
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN_WHATSAPP")
PHONE_NUMBER_ID = "471456926058403"
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"

# 🔹 URL de tu Chatbot FastAPI
CHATBOT_API_URL = "http://127.0.0.1:8000/chat/"  # Cambia esto si tu chatbot está en otro servidor

# 🔹 Verificación del Webhook (Meta lo requiere)
VERIFY_TOKEN = "TU_VERIFY_TOKEN"

@app.get("/webhook/")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)  # Meta espera un número como respuesta
    return {"error": "Invalid verification"}, 403

# 🔹 Recibir mensajes de WhatsApp y responder con el chatbot
@app.post("/webhook/")
async def handle_whatsapp_message(request: Request):
    data = await request.json()

    # Verificar si el mensaje es válido
    if "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                message_data = change.get("value", {}).get("messages", [])
                for message in message_data:
                    sender_id = message["from"]
                    user_message = message["text"]["body"]

                    # 🔹 Llamar al chatbot FastAPI para obtener respuesta
                    bot_response = requests.post(CHATBOT_API_URL, json={"question": user_message})
                    bot_reply_text = bot_response.json().get("response", "Lo siento, no pude procesar eso.")

                    # 🔹 Enviar la respuesta a WhatsApp
                    send_whatsapp_message(sender_id, bot_reply_text)

    return {"status": "received"}

# 🔹 Función para enviar mensajes a WhatsApp
def send_whatsapp_message(to, text):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(WHATSAPP_API_URL, headers=headers, json=payload)'''