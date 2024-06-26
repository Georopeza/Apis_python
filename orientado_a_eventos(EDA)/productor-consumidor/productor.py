from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import websockets

app = FastAPI()

class User(BaseModel):
    id: int
    email: str

@app.post("/register/")
async def register_user(user: User):
    # Emitir evento de registro de usuario
    await emit_event(user)
    return {"message": "User registered"}

async def emit_event(user: User):
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        await websocket.send(user.model_dump_json())