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
    audio_buffer = AudioBuffer()  # Initialize a new audio buffer for each connection

    try:
        while True:
            try:
                message = await websocket.receive()  # Wait for incoming WebSocket messages

                if message["type"] == "websocket.receive":
                    if "bytes" in message:
                        # Write the incoming audio bytes to the buffer
                        audio_buffer.write(message["bytes"])

                    elif "text" in message:
                        control = json.loads(message['text'])
                        if control.get('type') == 'end_stream':
                            # The stream has ended, convert buffered audio to a WAV file
                            wav_file = audio_buffer.get_wav_file()
                            logging.info(f"Audio saved to file: {wav_file}")

                            try:
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

                            except Exception as e:
                                logging.error(f"Processing error: {e}")
                                await websocket.send_json({
                                    'type': 'error',
                                    'message': str(e)
                                })

                            # Reset the audio buffer after each full interaction
                            audio_buffer = AudioBuffer()

            except WebSocketDisconnect:
                logging.info("Client disconnected")
                break  # Break the loop and stop receiving when the client disconnects

    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        await connection_manager.disconnect(websocket=websocket)

    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)