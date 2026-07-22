"""
Universal Blockchain Platform (UBP)

Module:
    WebSocket API

Purpose:
    WebSocket endpoints for real-time blockchain data.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any
import json

from core.logger import get_logger
from core.websocket.manager import WebSocketMessage, get_connection_manager
from core.websocket.events import get_event_emitter

logger = get_logger(__name__)


class WebSocketRouter:
    """
    WebSocket route handler.
    """

    def __init__(self):
        self.manager = get_connection_manager()
        self.emitter = get_event_emitter()

    async def handle_connection(self, websocket: WebSocket, channel: str = "global") -> None:
        """
        Handle a WebSocket connection.

        Parameters
        ----------
        websocket : WebSocket
            WebSocket connection.
        channel : str
            Channel to subscribe to.
        """
        await self.manager.connect(websocket, channel)
        logger.info(f"🔌 WebSocket connected to channel: {channel}")

        try:
            # Start event emitter if not running
            # await self.emitter.start()

            while True:
                # Receive messages from client
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    await self._handle_message(websocket, message, channel)
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "data": "Invalid JSON format"
                    }))

        except WebSocketDisconnect:
            await self.manager.disconnect(websocket, channel)
            logger.info(f"🔌 WebSocket disconnected from channel: {channel}")

    async def _handle_message(
        self,
        websocket: WebSocket,
        message: Dict[str, Any],
        channel: str
    ) -> None:
        """
        Handle a WebSocket message from client.

        Parameters
        ----------
        websocket : WebSocket
            WebSocket connection.
        message : dict
            Received message.
        channel : str
            Current channel.
        """
        msg_type = message.get("type")

        if msg_type == "subscribe":
            # Subscribe to a specific channel
            new_channel = message.get("channel", channel)
            await self.manager.connect(websocket, new_channel)
            await websocket.send_text(json.dumps({
                "type": "subscribed",
                "data": {"channel": new_channel}
            }))
            logger.info(f"📡 Client subscribed to: {new_channel}")

        elif msg_type == "unsubscribe":
            # Unsubscribe from a channel
            old_channel = message.get("channel", channel)
            await self.manager.disconnect(websocket, old_channel)
            await websocket.send_text(json.dumps({
                "type": "unsubscribed",
                "data": {"channel": old_channel}
            }))
            logger.info(f"📡 Client unsubscribed from: {old_channel}")

        elif msg_type == "ping":
            # Ping response
            await websocket.send_text(json.dumps({
                "type": "pong",
                "data": {"timestamp": message.get("timestamp")}
            }))

        else:
            await websocket.send_text(json.dumps({
                "type": "error",
                "data": f"Unknown message type: {msg_type}"
            }))


# Singleton instance
_router = None


def get_websocket_router() -> WebSocketRouter:
    """Get the WebSocket router instance."""
    global _router
    if _router is None:
        _router = WebSocketRouter()
    return _router
