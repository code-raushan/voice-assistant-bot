import logging
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from services.websocket_manager import WSConnectionManager
from services.audio_buffer import AudioBuffer

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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket=websocket)
    audio_buffer = AudioBuffer()

    try:
        while True:
            message = await websocket.receive()
            print(message)

    except Exception as e:
        logging.error(f"websocket err: {e}")
        connection_manager.disconnect(websocket=websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)