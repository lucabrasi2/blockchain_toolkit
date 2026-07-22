"""
Universal Blockchain Platform (UBP)

Module:
    WebSocket Manager

Purpose:
    Manage WebSocket connections for real-time blockchain data.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

import asyncio
import json
from typing import Dict, Set, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

from core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class WebSocketMessage:
    """WebSocket message structure."""
    type: str
    data: Any
    timestamp: str = None
    channel: str = "global"

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

    def to_json(self) -> str:
        return json.dumps(asdict(self))


class ConnectionManager:
    """
    WebSocket connection manager for real-time data.
    """

    def __init__(self):
        self.active_connections: Dict[str, Set[Any]] = {}
        self._lock = asyncio.Lock()
        self._subscriptions: Dict[str, Set[str]] = {}

    async def connect(self, websocket, channel: str = "global") -> None:
        """
        Connect a WebSocket client.

        Parameters
        ----------
        websocket : WebSocket
            WebSocket connection.
        channel : str
            Channel to subscribe to.
        """
        await websocket.accept()
        async with self._lock:
            if channel not in self.active_connections:
                self.active_connections[channel] = set()
            self.active_connections[channel].add(websocket)
        logger.info(f"✅ Client connected to channel: {channel}")

    async def disconnect(self, websocket, channel: str = "global") -> None:
        """
        Disconnect a WebSocket client.

        Parameters
        ----------
        websocket : WebSocket
            WebSocket connection.
        channel : str
            Channel to unsubscribe from.
        """
        async with self._lock:
            if channel in self.active_connections:
                self.active_connections[channel].discard(websocket)
                if not self.active_connections[channel]:
                    del self.active_connections[channel]
        logger.info(f"❌ Client disconnected from channel: {channel}")

    async def broadcast(
        self,
        message: WebSocketMessage,
        channel: str = "global"
    ) -> None:
        """
        Broadcast a message to all clients in a channel.

        Parameters
        ----------
        message : WebSocketMessage
            Message to broadcast.
        channel : str
            Channel to broadcast to.
        """
        async with self._lock:
            if channel not in self.active_connections:
                return

        disconnected = []
        for websocket in self.active_connections.get(channel, []):
            try:
                await websocket.send_text(message.to_json())
            except Exception:
                disconnected.append(websocket)

        # Clean up disconnected clients
        for websocket in disconnected:
            await self.disconnect(websocket, channel)

    async def send_to_client(
        self,
        websocket,
        message: WebSocketMessage
    ) -> None:
        """
        Send a message to a specific client.

        Parameters
        ----------
        websocket : WebSocket
            WebSocket connection.
        message : WebSocketMessage
            Message to send.
        """
        try:
            await websocket.send_text(message.to_json())
        except Exception as e:
            logger.error(f"Error sending message to client: {e}")

    def get_connection_count(self, channel: str = "global") -> int:
        """
        Get the number of active connections in a channel.

        Parameters
        ----------
        channel : str
            Channel name.

        Returns
        -------
        int
            Number of active connections.
        """
        return len(self.active_connections.get(channel, []))

    def get_channels(self) -> list:
        """
        Get all active channels.

        Returns
        -------
        list
            List of active channel names.
        """
        return list(self.active_connections.keys())


# Singleton instance
_manager = None


def get_connection_manager() -> ConnectionManager:
    """Get the WebSocket connection manager instance."""
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager
