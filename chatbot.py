import os
import mysql.connector
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
import pandas as pd
from db_config import connect_db
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure the API key is set correctly from the environment
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

# Function to load data from MySQL
def load_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM content")
    data = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(data, columns=["text"])
    
    return df

# Prepare LangChain with FAISS
def prepare_chatbot():
    df = load_data()
    
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(df["text"].tolist(), embeddings)
    
    return RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name="gpt-4", api_key=openai_api_key),
        retriever=vectorstore.as_retriever()
    )

# Initialize the chatbot
qa_chain = prepare_chatbot()

# Function to answer questions
def ask_question(question):
    return qa_chain.run(question)