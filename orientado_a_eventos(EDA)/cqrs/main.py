from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()

class UpdateOrderCommand(BaseModel):
    order_id: int
    status: str

orders = {}

@app.post("/update_order/")
async def update_order(cmd: UpdateOrderCommand):
    orders[cmd.order_id] = cmd.status
    return {"message": "Order updated"}

@app.get("/orders/")
async def get_orders(order_id: int = Query(..., description="ID of the order to retrieve")):
    if order_id in orders:
        return {"order_id": order_id, "status": orders[order_id]}
    else:
        return {"error": "Order not found"}
