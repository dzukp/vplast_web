import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from service import init_service
from logger_config import logging_config

import asyncio
import uvicorn


logging.config.dictConfig(logging_config)

app = FastAPI()
data_holders = init_service()


async def update_params():
    while True:
        await asyncio.sleep(2.0)
        for data_holder in data_holders.values():
            data_holder.update()


@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("templates/index.html")


@app.get("/api/get-params")
async def get_params(id: str):
    data_holders[id].update()
    data = data_holders[id].get_data()
    return JSONResponse(content=data)


app.mount("/", StaticFiles(directory="static"), name="static")


# @app.on_event("startup")
# async def startup_event():
#     loop = asyncio.get_event_loop()
#     loop.create_task(update_params())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
