from fastapi import FastAPI, WebSocket

app = FastAPI()
consumers = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    consumers.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for consumer in consumers:
                if consumer != websocket:
                    await consumer.send_text(data)
    except Exception as e:
        consumers.remove(websocket)
