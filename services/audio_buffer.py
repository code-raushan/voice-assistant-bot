import io
import wave
from utils import Config

class AudioBuffer:
    def __init__(self):
        self.buffer = io.BytesIO()
        self.is_complete = False

    def write(self, data):
        self.buffer.write(data)

    def get_wav_file(self):
        # Convert buffer to WAV file
        with wave.open(Config.INPUT_AUDIO, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(16000)  # 16kHz sample rate
            wav_file.writeframes(self.buffer.getvalue())
        return Config.INPUT_AUDIO
