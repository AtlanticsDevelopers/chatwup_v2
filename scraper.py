import requests
from bs4 import BeautifulSoup
from db_config import connect_db

# URL de la página web
URL = "http://www.vpmluxuryhomes.com/"

# Función para extraer datos de la web
def scrape_website(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Error al acceder a la página")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    sections = soup.find_all(["h1", "h2", "h3", "p"])  # Captura títulos y párrafos
    content = "\n".join([section.get_text(strip=True) for section in sections])
    
    return content

# Función para guardar datos en MySQL
def save_to_db(content):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO content (text) VALUES (%s)", (content,))
    
    conn.commit()
    conn.close()

# Ejecutar el scraping y guardar los datos
if __name__ == "__main__":
    content = scrape_website(URL)
    if content:
        save_to_db(content)
        print("✅ Datos guardados en MySQL")
        