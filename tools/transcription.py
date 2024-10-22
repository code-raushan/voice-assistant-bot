from groq import Groq
from utils import Config
import logging

def transcribe_audio(audio_file_path):
    # print("inside transcribe_audio_function"+audio_file_path)
    client = Groq(api_key=Config.GROQ_API_KEY)
    
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language='en',
            )
        
        # Log the entire response to inspect it
        logging.info(f"Groq transcription response: {transcription}")
        
        # Check if the 'text' attribute exists
        if hasattr(transcription, 'text'):
            return transcription.text
        else:
            logging.error("Transcription object does not have 'text' attribute")
            return None

    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        raise e
