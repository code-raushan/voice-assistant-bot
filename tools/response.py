from groq import Groq
from utils import Config


def generate_response(chat_history):
    client = Groq(api_key=Config.GROQ_API_KEY)

    response = client.chat.completions.create(
        model=Config.GROQ_MODEL,
        messages=chat_history
    )

    return response.choices[0].message.content