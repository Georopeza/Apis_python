import asyncio
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import EventModel, SessionLocal, get_db

# nueva forma de manejo de los eventos de arranque
# y parada de FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("va a crear el bus de eventos")
    asyncio.create_task(event_consumer())
    yield


app = FastAPI(lifespan=lifespan)

class Event(BaseModel):
    id: int
    name: str

# Estructura de datos para almacenar suscriptores
subscribers: List[WebSocket] = []

# Cola asincrónica para el bus de mensajes
event_queue = asyncio.Queue()

@app.post("/emit_event/")
async def emit_event(event: Event, db: Session = Depends(get_db)):
    db_event = EventModel(id=event.id, name=event.name)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    await event_queue.put(event)
    return {"message": "Event emitted"}

async def event_consumer():
    while True:
        event = await event_queue.get()
        for subscriber in subscribers:
            await subscriber.send_text(event.json())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    subscribers.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Mantiene la conexión abierta
    except Exception:
        subscribers.remove(websocket)

@app.get("/retrieve_events/")
async def retrieve_events(db: Session = Depends(get_db)):
    events = db.query(EventModel).all()
    return events