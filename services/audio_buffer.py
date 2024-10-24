import io
import wave
import logging
from pathlib import Path
from typing import Union

class AudioBuffer:
    def __init__(self, output_path: Union[str, Path] = "input.wav"):
        """
        Initialize AudioBuffer with configurable output path.
        
        Args:
            output_path: Path where the WAV file will be saved
        """
        self.buffer = io.BytesIO()
        self.output_path = Path(output_path)
        self.is_complete = False
        
        # Create parent directories if they don't exist
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
    def write(self, data: bytes) -> None:
        """
        Write audio data to the buffer.
        
        Args:
            data: Audio data bytes to write
        """
        try:
            self.buffer.write(data)
        except Exception as e:
            logging.error(f"Error writing to buffer: {e}")
            raise

    def get_wav_file(self) -> Path:
        """
        Convert buffer to WAV file and save it.
        
        Returns:
            Path to the saved WAV file
        """
        try:
            # Get the buffer content
            audio_data = self.buffer.getvalue()
            
            # Ensure we have data to write
            if not audio_data:
                raise ValueError("No audio data in buffer")

            # Write WAV file with proper audio parameters
            with wave.open(str(self.output_path), 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 2 bytes per sample
                wav_file.setframerate(16000)  # 16kHz sample rate
                wav_file.writeframes(audio_data)
            
            logging.info(f"Successfully saved WAV file to {self.output_path}")
            return self.output_path

        except Exception as e:
            logging.error(f"Error creating WAV file: {e}")
            raise

    def reset(self) -> None:
        """Reset the buffer to prepare for new audio data."""
        self.buffer = io.BytesIO()
        self.is_complete = False