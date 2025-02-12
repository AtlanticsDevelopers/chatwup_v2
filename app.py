from fastapi import FastAPI, Request
import os
from fastapi.responses import PlainTextResponse
import uvicorn
from pydantic import BaseModel
import httpx  # Use httpx for async HTTP requests
from chatbot import ask_question

# Configurar FastAPI
app = FastAPI()

# Modelo de datos para recibir preguntas
class Question(BaseModel):
    question: str
    
# Endpoint del chatbot
@app.post("/chat/")
async def chat(question: Question):
    respuesta = await ask_question(question.question)  # Ensure ask_question is async if it involves I/O
    return {"response": respuesta}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# 🔹 Credenciales de la API de Meta
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN_WHATSAPP")
PHONE_NUMBER_ID = "471456926058403"
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"

# 🔹 URL de tu Chatbot FastAPI
CHATBOT_API_URL = "http://localhost:10000/chat/"

# 🔹 Verificación del Webhook (Meta lo requiere)
VERIFY_TOKEN = "Atlantics2025"

@app.get("/webhook/", response_class=PlainTextResponse)
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge  # Returns plain text

    return "Invalid verification", 403

# 🔹 Recibir mensajes de WhatsApp y responder con el chatbot
@app.post("/webhook/")
async def handle_whatsapp_message(request: Request):
    data = await request.json()
    
    if "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                message_data = change.get("value", {}).get("messages", [])
                for message in message_data:
                    sender_id = message["from"]
                    user_message = message.get("text", {}).get("body", "")

                    # 🔹 Call the chatbot FastAPI
                    async with httpx.AsyncClient() as client:  # Use httpx.AsyncClient for async requests
                        bot_response = await client.post(CHATBOT_API_URL, json={"question": user_message})

                    # Extract response text safely
                    if bot_response.status_code == 200:
                        bot_reply_text = bot_response.json().get("response", "Lo siento, no pude procesar eso.")
                    else:
                        bot_reply_text = f"⚠️ Error {bot_response.status_code}: {bot_response.text}"

                    # Send the response to WhatsApp
                    await send_whatsapp_message(sender_id, bot_reply_text)

    return {"status": "received"}

# 🔹 Función para enviar mensajes a WhatsApp
async def send_whatsapp_message(to, text):
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

    async with httpx.AsyncClient() as client:
        response = await client.post(WHATSAPP_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"❌ ERROR sending message: {response.text}")