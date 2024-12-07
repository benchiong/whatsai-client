import traceback
from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI, Request

from starlette.middleware.cors import CORSMiddleware

from data_type.whatsai_card import CardDataModel
from misc.logger import logger
from .sockets import sio
from .router import router
from .router_model import router as model_path_router
from .router_websocket import router as socket_router
from .router_civitai import router as civitai_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        CardDataModel.fill_default_card_infos()
    except Exception as e:
        traceback.print_exc()
        print("fill_default_card_infos error:", e)
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

