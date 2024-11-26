from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from misc.logger import logger
from misc.websocket_manager import WebsocketManager

router = APIRouter()


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now().toString()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://127.0.0.1:8171/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@router.get("/")
async def get():
    return HTMLResponse(html)

@router.get("/test")
async def test():
    WebsocketManager.send_message_sync('test', message_type='text')

@router.get("/send_message_to_client/{client_id}")
async def send_message_to_client(client_id: str):
    await WebsocketManager.send_message('test message.', message_type='text', client_id=client_id)

@router.websocket('/{client_id}')
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    logger.debug("websocket: {}. client_id: {}".format(websocket, client_id))
    await WebsocketManager.connect(client_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await WebsocketManager.send_message(f"You wrote: {data}", message_type='text', websocket=websocket)
            await WebsocketManager.send_message(f"Client #{client_id} says: {data}", message_type='text')
    except WebSocketDisconnect:
        WebsocketManager.disconnect(client_id)
        await WebsocketManager.send_message(f"Client #{client_id} left the chat", message_type='text')