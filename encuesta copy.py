from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Definir las preguntas y respuestas con flujo paso a paso
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
                "Ambiente": "1.2",
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

# Modelo para manejar las preguntas y respuestas del usuario
class PreguntaUsuario(BaseModel):
    pregunta: str
    respuesta: str
    siguiente_pregunta: Optional[str] = None  # Esta es la nueva propiedad para la siguiente pregunta

# Función para obtener la siguiente pregunta basada en la respuesta del usuario
def obtener_respuesta(pregunta_usuario: PreguntaUsuario):
    # Si la pregunta es "fin", devolvemos el mensaje final
    if pregunta_usuario.pregunta.lower() == "fin":
        return preguntas_respuestas["fin"]["mensaje"], None
    
    # Buscar la respuesta en el flujo de preguntas
    pregunta_actual = preguntas_respuestas["preguntas"].get(pregunta_usuario.pregunta, None)
    
    if not pregunta_actual:
        return "Lo siento, no reconozco esa pregunta.", None

    # Verificar si la respuesta está en las opciones disponibles
    siguiente_pregunta = pregunta_actual["respuestas"].get(pregunta_usuario.respuesta, None)
    
    if siguiente_pregunta:
        if siguiente_pregunta == "fin":
            return preguntas_respuestas["fin"]["mensaje"], None
        else:
            # Retornar la siguiente pregunta basada en la respuesta
            siguiente_pregunta_obj = preguntas_respuestas["preguntas"].get(siguiente_pregunta, None)
            return siguiente_pregunta_obj["pregunta"], siguiente_pregunta
    else:
        return "Respuesta no válida, por favor elige una de las opciones disponibles.", None

# Endpoint para recibir preguntas y devolver respuestas automáticas
@app.post("/preguntar/")
async def preguntar(pregunta_usuario: PreguntaUsuario):
    # Obtener la respuesta y la siguiente pregunta
    respuesta, siguiente_pregunta = obtener_respuesta(pregunta_usuario)
    
    # Si existe una siguiente pregunta, incluirla en la respuesta
    if siguiente_pregunta:
        return {"respuesta": respuesta, "siguiente_pregunta": siguiente_pregunta}
    else:
        return {"respuesta": respuesta}