import uvicorn
from fastapi import FastAPI
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from ConnectionManager import ConnectionManager

app = FastAPI()

html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebSocket Chat</title>
</head>
<body>
    <h1>WebSocket Chat</h1>
    <div id="clientIdContainer">
        <input type="text" id="clientIdInput" placeholder="Enter your client ID"/>
        <button onclick="setClientId()">Set ID</button>
    </div>
    <div id="chat-container" style="display: none;">
        <h2>Your ID: <span id="ws-id"></span></h2>
        <ul id="messages"></ul>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
    </div>
    <script>
        var ws;

        function setClientId() {
            var clientId = document.getElementById('clientIdInput').value;
            if (!clientId) {
                alert('Please enter a valid client ID');
                return;
            }
            document.getElementById('ws-id').textContent = clientId;
            document.getElementById('chat-container').style.display = 'block';
            document.getElementById('clientIdContainer').style.display = 'none';
            ws = new WebSocket(`ws://localhost:8000/ws/${clientId}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages');
                var message = document.createElement('li');
                var content = document.createTextNode(event.data);
                message.appendChild(content);
                messages.appendChild(message);
                messages.scrollTop = messages.scrollHeight; // Scroll to bottom
            };
        }

        function sendMessage(event) {
            event.preventDefault();
            if (ws && ws.readyState === WebSocket.OPEN) {
                var input = document.getElementById("messageText");
                ws.send(input.value);
                input.value = '';
            } else {
                alert('WebSocket is not connected');
            }
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def index():
    return HTMLResponse(html)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")


if __name__ == "__main__":
    manager = ConnectionManager()
    uvicorn.run(app, host="0.0.0.0", port=8000)
