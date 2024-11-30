from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI, Request

from starlette.middleware.cors import CORSMiddleware

from data_type.whatsai_model_downloading_info import ModelDownloadingInfo
from misc.logger import logger
from tiny_db.init import initialize_dbs
from tiny_db.model_downloading_info import ModelDownloadInfoTable
from .sockets import sio
from .router import router
from .router_model import router as model_path_router, start_to_download
from .router_websocket import router as socket_router
from .router_civitai import router as civitai_router

def recovery_download_tasks():
    downloading_records = ModelDownloadInfoTable.get_all_downloading_records()
    for record in downloading_records:
        start_to_download(ModelDownloadingInfo(**record))

@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_dbs()
    recovery_download_tasks()
    yield


app = FastAPI(lifespan=lifespan)
app.logger = logger


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logger.info(f'Request url: {request.url}, Request-Method: {request.method}, Response-Status-Code:{response.status_code}')
    return response


app.include_router(router)
app.include_router(model_path_router, prefix='/model')
app.include_router(civitai_router, prefix='/civitai')
app.include_router(socket_router, prefix='/ws')


app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

app = socketio.ASGIApp(sio, app, socketio_path='/fastapi/sockets')

