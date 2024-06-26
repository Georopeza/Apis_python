"""
Este ejemplo usa Redis como lalibrería del manejo 
del publisher
"""

import aioredis
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
redis = aioredis.from_url("redis://localhost")

class Payment(BaseModel):
    id: int
    amount: float

@app.post("/payment/")
async def process_payment(payment: Payment):
    await redis.publish("payments", payment.model_dump_json())
    return {"message": "Payment processed"}