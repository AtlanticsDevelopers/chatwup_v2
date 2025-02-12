from fastapi import FastAPI, Request
import requests
import os
from fastapi.responses import PlainTextResponse
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

##WHATS APP
# 🔹 Credenciales de la API de Meta
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN_WHATSAPP")
PHONE_NUMBER_ID = "471456926058403"
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"

# 🔹 URL de tu Chatbot FastAPI
CHATBOT_API_URL = "https://chatwup-v2-9749.onrender.com/chat/"  # Cambia esto si tu chatbot está en otro servidor

# 🔹 Verificación del Webhook (Meta lo requiere)
VERIFY_TOKEN = "Atlantics2025"

@app.get("/webhook/", response_class=PlainTextResponse)
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    print(f"🔹 Incoming Verification Request: mode={mode}, token={token}, challenge={challenge}")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook Verified Successfully!")
        return challenge  # ✅ Returns plain text

    print(f"❌ Webhook Verification Failed! Expected token: {VERIFY_TOKEN}, Received token: {token}")
    return "Invalid verification", 403

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
    
    print(f"🔑 WhatsApp Access Token: {ACCESS_TOKEN}")  # Debug token  
    print(f"📤 Sending Message to {to}: {text}")  
    print(f"📝 WhatsApp API Response: {response.status_code}, {response.text}")  

    if response.status_code != 200:
        print(f"❌ ERROR sending message: {response.text}")
    
