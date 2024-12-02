from email import message_from_string
from pyexpat.errors import messages

import uvicorn
from fastapi import FastAPI, HTTPException
import asyncio
from LpuService import LpuService

app = FastAPI()

@app.get("/lpu")
def get_lpu_list():
    service = LpuService()
    data = service.get_names()
    if data:
        return {"names": data}
    raise HTTPException(status_code=404)

@app.get("/lpu/{name}")
def get_lpu_data(host):
    if not host:
        raise HTTPException(status_code=400)
    service = LpuService()
    data = service.get_lpu_data(host)
    if data:
        return {"data": data}
    raise HTTPException(status_code=400)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        host="127.0.0.1",
        port=52911
    )
