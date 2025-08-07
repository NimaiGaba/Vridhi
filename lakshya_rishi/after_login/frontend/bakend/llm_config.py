from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()  # Loads your .env file with GROQ_API_KEY

llm = ChatGroq(
    temperature=0.5,
    model_name="meta-llama/llama-4-scout-17b-16e-instruct",  
    groq_api_key=os.getenv("llama3_api_key")
)
# print('Hello')
