from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import aioredis


# nueva forma de manejo de los eventos de arranque
# y parada de FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis.initialize()    # equivalente al startup
    yield
    await redis.close()         # equivalente al shutdown


app = FastAPI(lifespan=lifespan) # se inyecta el manejo de eventos de arranque y parada

# acceso a la base de datos postgres
DATABASE_URL = "postgresql://user:password@localhost/dbname"
# instancia asyncrona de Redis, como Bus de Eventos
redis = aioredis.from_url("redis://localhost")

# Generación de la sesion de la DB
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# tabla events, para la persistencia de los eventos
class EventModel(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

Base.metadata.create_all(bind=engine)


# usando pydantic se crea el schema del evento
class Event(BaseModel):
    id: int
    name: str

# Estructura de datos en memoria para almacenar conexiones WebSocket
active_connections: List[WebSocket] = []


# método que crea y propaga el evento
@app.post("/emit_event/")
async def emit_event(event: Event):
    # persiste el evento en DB
    db = SessionLocal()
    db_event = EventModel(id=event.id, name=event.name)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    # publica el evento en el Bus
    await redis.publish("events", event.model_dump_json())

    # notifica a través de WS a los clientes conectados
    for connection in active_connections:
        await connection.send_text(event.model_dump_json())
    return {"message": "Event emitted"}


# permite obtener los eventos desde la DB
@app.get("/retrieve_events/")
async def retrieve_events():
    db = SessionLocal()
    events = db.query(EventModel).all()
    return events

# WS para realizar las notificaciones a los clientes conectados
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Manejar datos recibidos si es necesario
    except Exception as e:
        active_connections.remove(websocket)


# esta forma de manejo de eventos de arraque y parada
# están descontinuados ver arriba el método lifespan
"""
@app.on_event("startup")
async def startup_event():
    await redis.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    await redis.close()
"""