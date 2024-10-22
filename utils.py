import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    INPUT_AUDIO = "input.wav"
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")

