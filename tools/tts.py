import logging
from cartesia import Cartesia
import pyaudio
from utils import Config


def text_to_speech(text, output_file):
    try:
        client = Cartesia(api_key=Config.CARTESIA_API_KEY)
        voice_id = "f114a467-c40a-4db8-964d-aaba89cd08fa"
        voice = client.voices.get(id=voice_id)

        model_id = "sonic-english"

        output_format = {
            "container": "raw",
            "encoding": "pcm_f32le",
            "sample_rate": 44100,
        }

        p = pyaudio.PyAudio()
        rate = 44100

        stream = None

        # Generate and stream audio
        for output in client.tts.sse(
            model_id=model_id,
            transcript=text,
            voice_embedding=voice["embedding"],
            stream=True,
            output_format=output_format,
        ):
            buffer = output["audio"]

            if stream is None:
                stream = p.open(format=pyaudio.paFloat32, channels=1, rate=rate, output=True)

            # Write the audio data to the stream
            stream.write(buffer)
        
        if stream:
            stream.stop_stream()
            stream.close()
        p.terminate()
    except Exception as e:
        logging.error(f"Failed to convert text to speech: {e}")

    