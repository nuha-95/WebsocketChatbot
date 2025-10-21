from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

@app.get("/")
def get_chat():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chat Room</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #messages { border: 1px solid #ccc; height: 400px; overflow-y: scroll; padding: 10px; margin-bottom: 10px; }
            #messageInput { width: 70%; padding: 10px; }
            #sendBtn { padding: 10px 20px; }
            #clientId { width: 100px; padding: 5px; }
        </style>
    </head>
    <body>
        <h1>Chat Room</h1>
        <div>
            Client ID: <input type="number" id="clientId" value="" min="1" onchange="reconnect()">
        </div>
        <div id="messages"></div>
        <div>
            <input type="text" id="messageInput" placeholder="Type your message..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button id="sendBtn" onclick="sendMessage()">➤</button>
        </div>
        
        <script>
            let ws = null;
            let clientId = 1;
            
            function connect() {
                clientId = document.getElementById('clientId').value;
                if (ws) ws.close();
                ws = new WebSocket(`ws://127.0.0.1:8002/ws/${clientId}`);
                
                ws.onopen = function() {
                    addMessage(`Connected as Client #${clientId}`, 'system');
                    console.log('WebSocket connected');
                };
                
                ws.onmessage = function(event) {
                    console.log('Received:', event.data);
                    addMessage(event.data, 'received');
                };
                
                ws.onclose = function() {
                    addMessage('Disconnected', 'system');
                    console.log('WebSocket disconnected');
                };
                
                ws.onerror = function(error) {
                    console.log('WebSocket error:', error);
                };
            }
            
            function disconnect() {
                if (ws) {
                    ws.close();
                    ws = null;
                }
            }
            
            function reconnect() {
                disconnect();
                setTimeout(connect, 100);
            }
            
            // Auto-connect on page load with random ID
            window.onload = function() {
                const randomId = Math.floor(Math.random() * 1000) + 1;
                document.getElementById('clientId').value = randomId;
                connect();
            }
            
            function sendMessage() {
                const input = document.getElementById('messageInput');
                if (ws && input.value.trim()) {
                    ws.send(input.value);
                    input.value = '';
                }
            }
            
            function addMessage(message, type) {
                const messages = document.getElementById('messages');
                const div = document.createElement('div');
                div.style.margin = '5px 0';
                if (type === 'system') div.style.color = 'blue';
                else if (type === 'received') div.style.color = 'green';
                div.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
                messages.appendChild(div);
                messages.scrollTop = messages.scrollHeight;
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, client_id: int):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: int):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: str, client_id: int):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

    async def broadcast(self, message: str, sender_id: int):
        disconnected = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except:
                disconnected.append(client_id)
        for client_id in disconnected:
            self.disconnect(client_id)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket, client_id)
    await manager.broadcast(f"Client #{client_id} joined the chat", client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id}: {data}", client_id)
    except Exception as e:
        manager.disconnect(client_id)
        await manager.broadcast(f"Client #{client_id} left the chat", client_id)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)