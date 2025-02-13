from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Configura tu clave API de OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

app = FastAPI()

# Define las preguntas y respuestas (se puede almacenar en la base de datos)
preguntas_respuestas = {
    "preguntas": {
        "1": {
            "pregunta": "¿Cómo calificarías tu experiencia general con nosotros?",
            "respuestas": {
                "Bueno": "1.1",
                "Medio": "1.2",
                "Malo": "1.3"
            }
        },
        "1.1": {
            "pregunta": "¡Nos alegra mucho! ¿Qué fue lo que más disfrutaste?",
            "respuestas": {
                "Ambiente": "fin",
                "Servicio": "fin",
                "Comida": "fin"
            }
        },
        "1.2": {
            "pregunta": "Gracias por tu opinión. ¿En qué podemos mejorar?",
            "respuestas": {
                "Servicio": "fin",
                "Instalaciones": "fin"
            }
        },
        "1.3": {
            "pregunta": "Lamentamos que tu experiencia no haya sido la mejor. ¿Hubo algún problema en particular?",
            "respuestas": {
                "Limpieza": "fin",
                "Ruido": "fin",
                "Atención": "fin"
            }
        },
        "fin": {
            "mensaje": "Gracias por tu respuesta. ¡Esperamos verte pronto! 😊"
        }
    }
}

# Modelo para manejar las preguntas del usuario
class PreguntaUsuario(BaseModel):
    pregunta: str
    respuesta: str

# Crear el modelo de lenguaje de OpenAI
llm = ChatOpenAI(model="gpt-4", openai_api_key=openai_api_key)

# Conexión a LangChain para procesar la pregunta del usuario
def obtener_respuesta(pregunta_usuario: PreguntaUsuario):
    # Si la pregunta es "fin", devolvemos el mensaje de finalización
    if pregunta_usuario.pregunta.lower() == "fin":
        return preguntas_respuestas["fin"]["mensaje"]

    # Buscamos la pregunta que coincide con el mensaje del usuario
    for clave, valor in preguntas_respuestas["preguntas"].items():
        if valor["pregunta"].lower() in pregunta_usuario.pregunta.lower():  # Caso insensible
            respuestas = valor["respuestas"]
            # Verificamos si la respuesta coincide con las opciones definidas
            respuesta = respuestas.get(pregunta_usuario.respuesta, None)
            if respuesta:
                return respuesta
            else:
                # Si la respuesta no coincide, generamos una respuesta con GPT-4
                return f"Lo siento, no entendí esa respuesta. ¿Podrías responder con las opciones disponibles? Las opciones son: {', '.join(respuestas.keys())}"
    
    # Si no se encuentra una respuesta en las preguntas predeterminadas, generamos una respuesta con GPT-4
    prompt_template = """
    El usuario ha hecho la siguiente pregunta: "{pregunta}"
    Proporcióname una respuesta coherente y apropiada basada en una conversación amigable y profesional.
    """
    prompt = PromptTemplate(input_variables=["pregunta"], template=prompt_template)
    chain = LLMChain(llm=llm, prompt=prompt)
    
    respuesta_generada = chain.run(pregunta_usuario.pregunta)
    return respuesta_generada

# Endpoint para recibir preguntas y devolver respuestas
@app.post("/preguntar/")
async def preguntar(pregunta_usuario: PreguntaUsuario):
    # Utilizamos LangChain para procesar la pregunta
    respuesta = obtener_respuesta(pregunta_usuario)
    return {"respuesta": respuesta}