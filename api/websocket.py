"""
Universal Blockchain Platform (UBP)

Module:
    WebSocket API

Purpose:
    WebSocket endpoints for real-time blockchain data.

Author:
    Jaramogi Diddy

Project:
    Universal Blockchain Platform (UBP)

Version:
    2.0.0
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from fastapi import WebSocket, WebSocketDisconnect

from core.logger import get_logger
from core.websocket.events import get_event_emitter
from core.websocket.manager import get_connection_manager


logger = get_logger(__name__)


# =============================================================================
# Constants
# =============================================================================

DEFAULT_CHANNEL = "global"

MESSAGE_TYPE_SUBSCRIBE = "subscribe"
MESSAGE_TYPE_UNSUBSCRIBE = "unsubscribe"
MESSAGE_TYPE_PING = "ping"

RESPONSE_TYPE_SUBSCRIBED = "subscribed"
RESPONSE_TYPE_UNSUBSCRIBED = "unsubscribed"
RESPONSE_TYPE_PONG = "pong"
RESPONSE_TYPE_ERROR = "error"


# =============================================================================
# WebSocket Router
# =============================================================================

class WebSocketRouter:
    """
    WebSocket route handler.

    This class acts as the API-layer adapter between FastAPI WebSocket
    connections and the shared UBP WebSocket infrastructure.

    Connection management is delegated to:
        core.websocket.manager

    Event management is delegated to:
        core.websocket.events
    """

    def __init__(self) -> None:
        self.manager = get_connection_manager()
        self.emitter = get_event_emitter()

    # =========================================================================
    # Connection Lifecycle
    # =========================================================================

    async def handle_connection(
        self,
        websocket: WebSocket,
        channel: str = DEFAULT_CHANNEL,
    ) -> None:
        """
        Handle a WebSocket connection.

        Parameters
        ----------
        websocket:
            Active FastAPI WebSocket connection.

        channel:
            Initial channel to subscribe the connection to.
        """
        await self.manager.connect(
            websocket,
            channel,
        )

        logger.info(
            "WebSocket connected to channel: %s",
            channel,
        )

        try:
            while True:
                data = await websocket.receive_text()

                await self._process_client_message(
                    websocket=websocket,
                    data=data,
                    channel=channel,
                )

        except WebSocketDisconnect:
            await self._disconnect(
                websocket=websocket,
                channel=channel,
            )

    async def _disconnect(
        self,
        websocket: WebSocket,
        channel: str,
    ) -> None:
        """
        Disconnect a WebSocket from its active channel.
        """
        try:
            await self.manager.disconnect(
                websocket,
                channel,
            )

        finally:
            logger.info(
                "WebSocket disconnected from channel: %s",
                channel,
            )

    # =========================================================================
    # Message Processing
    # =========================================================================

    async def _process_client_message(
        self,
        websocket: WebSocket,
        data: str,
        channel: str,
    ) -> None:
        """
        Parse and dispatch a message received from the client.

        Invalid JSON is handled at the WebSocket protocol layer and does not
        terminate the connection.
        """
        try:
            message = json.loads(data)

        except json.JSONDecodeError:
            await self._send_error(
                websocket,
                "Invalid JSON format",
            )
            return

        if not isinstance(message, dict):
            await self._send_error(
                websocket,
                "WebSocket message must be a JSON object",
            )
            return

        await self._handle_message(
            websocket=websocket,
            message=message,
            channel=channel,
        )

    async def _handle_message(
        self,
        websocket: WebSocket,
        message: Dict[str, Any],
        channel: str,
    ) -> None:
        """
        Handle a WebSocket message from a client.

        Supported message types:

            subscribe
            unsubscribe
            ping
        """
        message_type = message.get("type")

        if message_type == MESSAGE_TYPE_SUBSCRIBE:
            await self._handle_subscribe(
                websocket=websocket,
                message=message,
                channel=channel,
            )
            return

        if message_type == MESSAGE_TYPE_UNSUBSCRIBE:
            await self._handle_unsubscribe(
                websocket=websocket,
                message=message,
                channel=channel,
            )
            return

        if message_type == MESSAGE_TYPE_PING:
            await self._handle_ping(
                websocket=websocket,
                message=message,
            )
            return

        await self._send_error(
            websocket,
            f"Unknown message type: {message_type}",
        )

    # =========================================================================
    # Subscribe / Unsubscribe
    # =========================================================================

    async def _handle_subscribe(
        self,
        websocket: WebSocket,
        message: Dict[str, Any],
        channel: str,
    ) -> None:
        """
        Subscribe a WebSocket connection to a channel.
        """
        new_channel = message.get(
            "channel",
            channel,
        )

        if not isinstance(new_channel, str):
            await self._send_error(
                websocket,
                "Channel must be a string",
            )
            return

        new_channel = new_channel.strip()

        if not new_channel:
            await self._send_error(
                websocket,
                "Channel cannot be empty",
            )
            return

        await self.manager.connect(
            websocket,
            new_channel,
        )

        await self._send_json(
            websocket,
            {
                "type": RESPONSE_TYPE_SUBSCRIBED,
                "data": {
                    "channel": new_channel,
                },
            },
        )

        logger.info(
            "Client subscribed to: %s",
            new_channel,
        )

    async def _handle_unsubscribe(
        self,
        websocket: WebSocket,
        message: Dict[str, Any],
        channel: str,
    ) -> None:
        """
        Unsubscribe a WebSocket connection from a channel.
        """
        old_channel = message.get(
            "channel",
            channel,
        )

        if not isinstance(old_channel, str):
            await self._send_error(
                websocket,
                "Channel must be a string",
            )
            return

        old_channel = old_channel.strip()

        if not old_channel:
            await self._send_error(
                websocket,
                "Channel cannot be empty",
            )
            return

        await self.manager.disconnect(
            websocket,
            old_channel,
        )

        await self._send_json(
            websocket,
            {
                "type": RESPONSE_TYPE_UNSUBSCRIBED,
                "data": {
                    "channel": old_channel,
                },
            },
        )

        logger.info(
            "Client unsubscribed from: %s",
            old_channel,
        )

    # =========================================================================
    # Ping / Pong
    # =========================================================================

    async def _handle_ping(
        self,
        websocket: WebSocket,
        message: Dict[str, Any],
    ) -> None:
        """
        Respond to a client ping message.
        """
        await self._send_json(
            websocket,
            {
                "type": RESPONSE_TYPE_PONG,
                "data": {
                    "timestamp": message.get(
                        "timestamp"
                    ),
                },
            },
        )

    # =========================================================================
    # Response Helpers
    # =========================================================================

    @staticmethod
    async def _send_json(
        websocket: WebSocket,
        payload: Dict[str, Any],
    ) -> None:
        """
        Serialize and send a JSON response to the client.
        """
        await websocket.send_text(
            json.dumps(payload)
        )

    async def _send_error(
        self,
        websocket: WebSocket,
        message: str,
    ) -> None:
        """
        Send a standardized WebSocket error response.
        """
        await self._send_json(
            websocket,
            {
                "type": RESPONSE_TYPE_ERROR,
                "data": message,
            },
        )


# =============================================================================
# Singleton
# =============================================================================

_router: Optional[WebSocketRouter] = None


def get_websocket_router() -> WebSocketRouter:
    """
    Return the shared WebSocket router instance.

    The router is initialized lazily so importing this module does not
    unnecessarily initialize the WebSocket infrastructure.
    """
    global _router

    if _router is None:
        _router = WebSocketRouter()

    return _router