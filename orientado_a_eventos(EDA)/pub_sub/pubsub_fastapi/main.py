from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from typing import Dict, Set

@asynccontextmanager
async def lifespan(app: FastAPI):
    channel_name = "mi_canal"
    channels[channel_name] = set()
    yield

app = FastAPI(lifespan=lifespan)

# Estructura de datos para almacenar canales y suscriptores
channels: Dict[str, Set[WebSocket]] = {}

@app.websocket("/ws/{channel}")
async def websocket_endpoint(channel: str, websocket: WebSocket):
    await websocket.accept()
    if channel not in channels:
        channels[channel] = set()
    channels[channel].add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # Publicar mensaje en el canal
            for subscriber in channels.get(channel, []):
                await subscriber.send_text(data)
    except Exception as e:
        channels[channel].remove(websocket)
        await websocket.close()

# @app.on_event("startup")
# async def startup_event():
#     channel_name = "mi_canal"
#     channels[channel_name] = set()

# Publicar mensaje en el canal
async def publish_message(channel: str, message: str):
    for subscriber in channels.get(channel, []):
        await subscriber.send_text(message)

# Ejemplo de uso
@app.get("/")
async def read_root():
    await publish_message("mi_canal", "¡Hola, mundo!")
    return {"message": "Message published to mi_canal"}

# Ejecutar la aplicación con: uvicorn main:app --reload
