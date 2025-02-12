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
##WHATS APP
# 🔹 Credenciales de la API de Meta
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN_WHATSAPP")
PHONE_NUMBER_ID = "471456926058403"
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"

# 🔹 URL de tu Chatbot FastAPI
CHATBOT_API_URL = "https://chatwup-v2-9749.onrender.com/chat/"  # Cambia esto si tu chatbot está en otro servidor

# 🔹 Verificación del Webhook (Meta lo requiere)
VERIFY_TOKEN = "Atlantics2025"

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
    print("🔹 Webhook recibido:", data)  # Verificar si llega información desde WhatsApp

    if "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                message_data = change.get("value", {}).get("messages", [])
                for message in message_data:
                    sender_id = message["from"]
                    user_message = message["text"]["body"]

                    print(f"📩 Mensaje recibido de {sender_id}: {user_message}")  # Verificar si se detecta el mensaje

                    # Llamar al chatbot FastAPI
                    bot_response = requests.post(CHATBOT_API_URL, json={"question": user_message})
                    bot_reply_text = bot_response.json().get("response", "Lo siento, no pude procesar eso.")

                    print(f"🤖 Respuesta del chatbot: {bot_reply_text}")  # Verificar si el chatbot responde

                    # Enviar respuesta a WhatsApp
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
    
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    print("WhatsApp API Response:", response.status_code, response.text)  # 🔹 Agrega esta línea para depurar