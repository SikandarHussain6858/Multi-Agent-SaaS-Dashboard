from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept the WebSocket connection and add it to the active list."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove the WebSocket connection from the active list."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a text message to a specific WebSocket client."""
        await websocket.send_text(message)

    async def send_personal_json(self, data: dict, websocket: WebSocket):
        """Send a JSON payload to a specific WebSocket client."""
        await websocket.send_json(data)

    async def broadcast(self, message: str):
        """Broadcast a text message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"[!] Failed to send broadcast message: {e}")

    async def broadcast_json(self, data: dict):
        """Broadcast a JSON payload to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                print(f"[!] Failed to send broadcast json: {e}")

# Create a global instance to be used across the app
manager = ConnectionManager()
