import asyncio
from typing import Literal

from fastapi import WebSocket

from misc.logger import logger


class WebsocketManager:
    client_connections: dict[str, WebSocket] = {}
    loop = asyncio.get_event_loop()

    logger.debug("WebsocketManager Loop: {}".format(loop))

    @classmethod
    async def connect(cls, client_id: str, websocket: WebSocket):
        await websocket.accept()
        cls.client_connections[client_id] = websocket
        logger.debug("client_connections: {}".format(cls.client_connections))

    @classmethod
    def disconnect(cls, client_id: str):
        cls.client_connections.pop(client_id)

    @classmethod
    async def send_message(cls,
                           message: str | dict | bytes | bytearray,
                           message_type: Literal['text', 'json', 'bytes'],
                           websocket: WebSocket | None = None,
                           client_id: str | None = None,
                           ):
        websocket = websocket if websocket else cls.client_connections.get(client_id)
        if not websocket:
            for ws in cls.client_connections.values():
                await cls._send_message(ws, message, message_type)
        else:
            await cls._send_message(websocket, message, message_type)

    @classmethod
    async def _send_message(cls,
                            websocket: WebSocket,
                            message: str | dict | bytes | bytearray,
                            message_type: Literal['text', 'json', 'bytes']
                            ):
        if message_type == 'text':
            await websocket.send_text(message)
        elif message_type == 'json':
            await websocket.send_json(message)
        elif message_type == 'bytes':
            await websocket.send_bytes(message)
        else:
            raise Exception("Not supported message type: {}".format(message_type))

    @classmethod
    def send_message_sync(cls,
                          message: str,
                          message_type: Literal['text', 'json', 'bytes'],
                          websocket: WebSocket | None = None,
                          client_id: str | None = None,
                          ):
        cls.loop.create_task(cls.send_message(message, message_type, websocket, client_id))

