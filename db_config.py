import mysql.connector

# Función para conectar a la base de datos MySQL
def connect_db():
      return mysql.connector.connect(
        host="46.202.198.207",
        user="u723373843_rene",  # Cambia esto por tu usuario
        password="Atlantics01!",  # Cambia esto por tu contraseña
        database="u723373843_DB_WEB_ATLANTI"
    )
'''  host="localhost",
        user="Atlantics",  # Cambia esto por tu usuario
        password="Atl@ntics02!",  # Cambia esto por tu contraseña
        database="chatbot_db" '''