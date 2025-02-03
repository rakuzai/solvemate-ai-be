from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    SESSION_TIMEOUT = 60 * 60 * 12  # 12 hours in seconds
    MODEL_NAME = "llama-3.3-70b-versatile"