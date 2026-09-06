from fastapi import WebSocket


class ConnectionManager:
    """Tracks live WebSocket connections keyed by an arbitrary channel id
    (e.g. a simulation run id) so simulation workers can broadcast progress.
    Simulation modules wire into this later; nothing subscribes yet.
    """

    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, channel: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(channel, []).append(websocket)

    def disconnect(self, channel: str, websocket: WebSocket) -> None:
        connections = self._connections.get(channel, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            self._connections.pop(channel, None)

    async def broadcast(self, channel: str, message: dict) -> None:
        for websocket in self._connections.get(channel, []):
            await websocket.send_json(message)


connection_manager = ConnectionManager()
