from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from db_config import connect_db

# URL of the website to scrape
URL = "https://www.airbnb.mx/rooms/768231605693454788?_set_bev_on_new_domain=1739759856_EAMmY2ZGJlMDQ1MT&source_impression_id=p3_1739759858_P32IpZcZpGjISJKD"

# FastAPI app instance
app = FastAPI()

# Function to scrape the website
def scrape_website(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Error accessing the page")
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    sections = soup.find_all(["h1", "h2", "h3", "p"])  # Capture headings and paragraphs
    content = "\n".join([section.get_text(strip=True) for section in sections])
    return content

# Function to save data to MySQL
def save_to_db(content):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO content (text) VALUES (%s)", (content,))
    conn.commit()
    conn.close()

# Endpoint to trigger the scraping and saving process
@app.get("/scrape")
def scrape_and_save():
    content = scrape_website(URL)
    if content:
        save_to_db(content)
        return {"message": "✅ Data saved to MySQL"}
    else:
        return {"message": "❌ Error obtaining data"}