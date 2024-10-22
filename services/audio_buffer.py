import io
import wave
from utils import Config


class AudioBuffer:
    def __init__(self) -> None:
        self.buffer = io.BytesIO()
        self.is_complete = False

    def write(self, data):
        self.buffer.write(data)

    def get_wav_file(self):
        with wave.open(Config.INPUT_AUDIO, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(self.buffer.getvalue())
        return Config.INPUT_AUDIO
