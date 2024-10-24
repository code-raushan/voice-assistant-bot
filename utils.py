import logging
import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    INPUT_AUDIO = "input.wav"
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")
    GROQ_MODEL = "llama-3.1-8b-instant"


def delete_file(file_path):
    try:
        os.remove(file_path)
        logging.info(f"Deleted file: {file_path}")
    except FileNotFoundError:
        logging.warning(f"File not found: {file_path}")
    except PermissionError:
        logging.error(f"Permission denied when trying to delete this file: {file_path}")
    except OSError as e:
        logging.error(f"Error deleting file {file_path}: {e}")