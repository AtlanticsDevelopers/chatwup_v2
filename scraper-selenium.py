from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import mysql.connector

# Set up the WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run headless mode (no browser window)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL of the website to scrape
URL = "https://www.airbnb.mx/rooms/768231605693454788?_set_bev_on_new_domain=1739759856_EAMmY2ZGJlMDQ1MT&source_impression_id=p3_1739759858_P32IpZcZpGjISJKD"

# Function to connect to the MySQL database
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="Atlantics",  # Cambia esto por tu usuario
        password="Atl@ntics02!",  # Cambia esto por tu contraseña
        database="chatbot_db" 
    )

# Navigate to the page
driver.get(URL)

# Wait for the page to load
time.sleep(5)

# Example of extracting data after the page has loaded
try:
    title = driver.find_element(By.CSS_SELECTOR, 'h1._14i3z6h').text
    description = driver.find_element(By.CSS_SELECTOR, 'div._1d2f3p3').text
    price = driver.find_element(By.CSS_SELECTOR, 'span._tyxjp1').text
except Exception as e:
    print(f"Error extracting data: {e}")
    title = description = price = "N/A"

# Function to save the scraped data to MySQL
def save_to_db(title, description, price):
    conn = connect_db()
    cursor = conn.cursor()

    # Insert the scraped data into the MySQL database
    cursor.execute("""
        INSERT INTO airbnb_data (title, description, price)
        VALUES (%s, %s, %s)
    """, (title, description, price))

    conn.commit()
    conn.close()

# Save the scraped data to MySQL
save_to_db(title, description, price)

# Print the data (optional)
print(f"Title: {title}\nDescription: {description}\nPrice: {price}")

# Close the driver
driver.quit()