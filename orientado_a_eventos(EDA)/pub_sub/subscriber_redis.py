import aioredis
from fastapi import FastAPI

app = FastAPI()
redis = aioredis.from_url("redis://localhost")

@app.on_event("startup")
async def startup_event():
    pubsub = redis.pubsub()
    await pubsub.subscribe("payments")
    async for message in pubsub.listen():
        if message['type'] == 'message':
            payment = message['data']
            # Procesar el pago (por ejemplo, enviar una notificación)