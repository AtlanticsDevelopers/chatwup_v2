import mysql.connector

# Función para conectar a la base de datos MySQL
def connect_db():
      return mysql.connector.connect(
        host="localhost",
        user="Atlantics",  # Cambia esto por tu usuario
        password="Atl@ntics02!",  # Cambia esto por tu contraseña
        database="chatbot_db"
    )
      