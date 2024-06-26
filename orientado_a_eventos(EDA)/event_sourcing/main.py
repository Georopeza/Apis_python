from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

class OrderEvent(BaseModel):
    order_id: int
    event_type: str
    data: dict

events = []

@app.post("/orders/")
async def create_order(event: OrderEvent):
    events.append(event)
    return {"message": "Event stored"}

@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    order_events = [e for e in events if e.order_id == order_id]
    return {"events": order_events}
