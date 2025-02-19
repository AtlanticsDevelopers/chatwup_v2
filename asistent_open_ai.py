from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationSummaryMemory
from fastapi import FastAPI, Request
import os
import json
from fastapi.responses import PlainTextResponse
import uvicorn
from pydantic import BaseModel
from pydantic import BaseModel
import httpx  # Use httpx for async HTTP requests

# Cargar instrucciones del asistente
instructions = {
    "nombre": "URA Bot",
    "personalidad": "Profesional, amigable y confiable",
    "tono": "Claro, directo y con un toque empático",
    "estilo_respuesta": "Breve pero informativo, proporcionando enlaces o sugerencias cuando sea necesario",
    "objetivo": "Brindar información detallada sobre los productos de URAMX.com, resolver dudas sobre precios, disponibilidad, envíos, métodos de pago y políticas de devolución. Además, proporcionar soporte en el proceso de compra.",
    "contexto_comunicacion": "Canales de operación: WhatsApp y el sitio web de URAMX.com. Modo de respuesta: Responder consultas en tiempo real y guiar a los usuarios en su experiencia de compra.",
    "pasos_interaccion": """
1. Saludar amablemente y presentarte.
2. Escuchar activamente y responder a las preguntas del cliente. Utiliza el repositorio de preguntas frecuentes y la información sobre la empresa para proporcionar respuestas precisas.
3. Identificar el interés en los productos o servicios. Si el cliente muestra interés claro en un producto o desea ser contactado por un agente de ventas, ejecuta la función "Change stage to Interesado - Ventas".
4. Escalar casos complejos. Si el cliente tiene dudas avanzadas fuera de tu alcance, ofrece contacto con un ejecutivo de la empresa y, si lo solicita, ejecuta la función "Change stage to Asistencia Humana".
""",
    "casos_posibles": """
1. Consulta de productos: Precio, beneficios, ingredientes, uso recomendado.
2. Disponibilidad y envíos: Zonas de cobertura, tiempos de entrega, costos de envío.
3. Métodos de pago: Tarjetas de crédito/débito, PayPal, transferencias.
4. Devoluciones y cambios: Política, tiempos y proceso de solicitud.
5. Soporte en la compra: Problemas con la plataforma, fallas en el pago.
""",
    "comportamiento_predefinido": """
En caso de consultas fuera de tu alcance, sugiere contacto con soporte.
No proporciones información no confirmada o especulativa.
Mantén siempre un tono profesional y respetuoso.
""",
    "informacion_tienda": """
Nombre: URAMX.com
Especialidad: Venta de productos naturales.
Sitio web: URAMX.com
Horarios de atención: Lunes a viernes de 9:00 AM a 6:00 PM.
Contacto: WhatsApp, correo electrónico, redes sociales.
""",
    "informacion_productos": """
Catálogo de productos:
- URA Gotero Remedio Universal 15ml - $300.00
- URA Roll-On Remedio Universal 10ml - $200.00
- URA Bálsamo Remedio Universal 5g - $60.00
- URA Gotero Remedio Universal 2pack 15ml - $480.00
- URA Roll-On Remedio Universal 2pack 10ml - $320.00
- URA Bálsamo Remedio Universal 10pack 5g - $450.00
- URA Multipack Remedio Universal - $450.00
""",
    "informacion_clave": """
- Todos los productos son naturales y seguros para su uso.
- Pueden ser utilizados para diversas aplicaciones terapéuticas.
- Envío a todo México con diferentes opciones de entrega.
- Promociones y descuentos en compras por volumen.
""",
    "formato_respuesta": """
- Mensajes breves, estructurados y con posibilidad de enlaces a la tienda.
- Uso de listas para facilitar la lectura.
- Personalización con el nombre del usuario si está disponible.
""",
    "no_hacer": """
- No des información errónea sobre disponibilidad o precios.
- No hagas promesas de entrega sin verificar.
- No compartas datos personales de clientes.
"""
}

# Crear prompt con instrucciones incorporadas
prompt_template = PromptTemplate.from_template("""
Eres {nombre}, un asistente {personalidad}.
Tu tono de comunicación es {tono} y tu estilo de respuesta es {estilo_respuesta}.
Tu objetivo es: {objetivo}
El contexto de comunicación es el siguiente: {contexto_comunicacion}
Los pasos para interactuar con el cliente son los siguientes:
{pasos_interaccion}
Los casos posibles de consulta son:
{casos_posibles}
El comportamiento predefinido es:
{comportamiento_predefinido}
La información clave sobre la tienda es:
{informacion_tienda}
La información sobre los productos es:
{informacion_productos}
La información clave sobre los productos es:
{informacion_clave}
El formato de respuesta es:
{formato_respuesta}
Lo que no debes hacer es:
{no_hacer}
Responde la siguiente pregunta manteniendo estas características:

Pregunta: {question}
""")

# Instancia del modelo de OpenAI
llm = ChatOpenAI(model_name="gpt-4", temperature=0.5)

# Memoria para mantener contexto de la conversación
memory = ConversationSummaryMemory(llm=llm)

# Crear API con FastAPI
app = FastAPI()

@app.post("/chat/")
async def chat_endpoint(query: dict):
    question = query.get("question", "")
    
    # Crear mensaje con contexto
    formatted_prompt = prompt_template.format(
        nombre=instructions["nombre"],
        personalidad=instructions["personalidad"],
        tono=instructions["tono"],
        estilo_respuesta=instructions["estilo_respuesta"],
        objetivo=instructions["objetivo"],
        contexto_comunicacion=instructions["contexto_comunicacion"],
        pasos_interaccion=instructions["pasos_interaccion"],
        casos_posibles=instructions["casos_posibles"],
        comportamiento_predefinido=instructions["comportamiento_predefinido"],
        informacion_tienda=instructions["informacion_tienda"],
        informacion_productos=instructions["informacion_productos"],
        informacion_clave=instructions["informacion_clave"],
        formato_respuesta=instructions["formato_respuesta"],
        no_hacer=instructions["no_hacer"],
        question=question
    )

    # Obtener respuesta del modelo
    response = llm.predict(formatted_prompt)
    
    return {"response": response}

'''ASISTENTE BY WHATS APP'''
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