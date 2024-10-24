import json
import logging
from pathlib import Path
from colorama import Fore
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from services.websocket_manager import WSConnectionManager
from services.audio_buffer import AudioBuffer
from tools.transcription import transcribe_audio
from tools.response import generate_response
from tools.tts import text_to_speech
from utils import delete_file

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(title="Voice Assistant Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connection_manager = WSConnectionManager()

static_dir = Path("static")
static_dir.mkdir(exist_ok=True)



@app.get("/")
async def get_index():
    """Serve the index.html file"""
    return FileResponse("static/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket=websocket)

    chat_history = [
        {"role": "system", "content": """ You are a helpful Assistant called Verbi. 
         You are friendly and fun and you will help the users with their requests.
         Your answers are short and concise. """}
    ]
    
    # Create input directory if it doesn't exist
    input_dir = Path("input")
    input_dir.mkdir(exist_ok=True)
    
    # Initialize audio buffer with path in the input directory
    audio_buffer = AudioBuffer(output_path=input_dir / "input.wav")
    message_counter = 0

    try:
        while True:
            try:
                message = await websocket.receive()

                if message["type"] == "websocket.receive":
                    message_counter += 1
                    logging.info(f"Receiving data chunk {message_counter}")
                    
                    if "bytes" in message:
                        # Write the incoming audio bytes to the buffer
                        try:
                            audio_buffer.write(message["bytes"])
                        except Exception as e:
                            logging.error(f"Error writing audio chunk: {e}")
                            await websocket.send_json({
                                'type': 'error',
                                'message': 'Failed to process audio chunk'
                            })

                    elif "text" in message:
                        control = json.loads(message['text'])
                        if control.get('type') == 'end_stream':
                            try:
                                # Convert buffered audio to WAV file
                                wav_file = audio_buffer.get_wav_file()
                                logging.info(f"Audio saved to file: {wav_file}")

                                # Perform transcription
                                user_input = transcribe_audio(audio_file_path=wav_file)

                                if not user_input:
                                    await websocket.send_json({
                                        'type': 'error',
                                        'message': 'No transcription available'
                                    })
                                else:
                                    logging.info(Fore.GREEN + f"Transcription: {user_input}" + Fore.RESET)
                                    await websocket.send_json({
                                        'type': 'transcription',
                                        'text': user_input
                                    })

                                chat_history.append({"role": "user", "content": user_input})

                                # Generate response
                                response_text = generate_response(chat_history=chat_history)

                                chat_history.append({"role": "assistant", "content": response_text})

                                await websocket.send_json({
                                    'type': 'response',
                                    'text': response_text
                                })

                                output_file = 'output.mp3'

                                text_to_speech(text=response_text, output_file=output_file)

                                with open(output_file, 'rb') as audio_file:
                                    audio_data = audio_file.read()
                                    await websocket.send_bytes(audio_data)

                                delete_file(output_file)

                            except Exception as e:
                                logging.error(f"Processing error: {e}")
                                await websocket.send_json({
                                    'type': 'error',
                                    'message': str(e)
                                })

                            # Reset the audio buffer after processing
                            audio_buffer.reset()

            except WebSocketDisconnect:
                logging.info("Client disconnected")
                break

    except Exception as e:
        logging.error(f"WebSocket error: {e}")

    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)