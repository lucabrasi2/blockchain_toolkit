"""
Universal Blockchain Platform (UBP)

Module:
    WebSocket Events

Purpose:
    Real-time blockchain event handlers.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from core.logger import get_logger
from core.websocket.manager import WebSocketMessage, get_connection_manager
from ethereum.connection import get_connection
from ethereum.blocks import get_block

logger = get_logger(__name__)


class BlockchainEventEmitter:
    """
    Emit real-time blockchain events via WebSocket.
    """

    def __init__(self):
        self.manager = get_connection_manager()
        self._running = False
        self._tasks = []

    async def start(self) -> None:
        """Start the event emitter."""
        if self._running:
            return
        self._running = True
        logger.info("🚀 Blockchain event emitter started")

        # Start monitoring tasks
        self._tasks.append(asyncio.create_task(self._monitor_new_blocks()))
        self._tasks.append(asyncio.create_task(self._monitor_pending_transactions()))

    async def stop(self) -> None:
        """Stop the event emitter."""
        self._running = False
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        logger.info("🛑 Blockchain event emitter stopped")

    async def _monitor_new_blocks(self) -> None:
        """Monitor and broadcast new blocks."""
        last_block = 0

        while self._running:
            try:
                # Get latest block
                block_data = get_block("latest")
                if block_data and "error" not in block_data:
                    block_number = block_data.get("number", 0)

                    if block_number > last_block:
                        last_block = block_number
                        message = WebSocketMessage(
                            type="new_block",
                            data={
                                "number": block_number,
                                "hash": block_data.get("hash"),
                                "timestamp": block_data.get("timestamp"),
                                "transaction_count": block_data.get("transaction_count", 0),
                                "miner": block_data.get("miner"),
                            },
                            channel="blocks"
                        )
                        await self.manager.broadcast(message, channel="blocks")
                        logger.info(f"📦 New block broadcast: {block_number}")

                await asyncio.sleep(3)  # Check every 3 seconds

            except Exception as e:
                logger.error(f"Error monitoring blocks: {e}")
                await asyncio.sleep(5)

    async def _monitor_pending_transactions(self) -> None:
        """Monitor pending transactions (mempool)."""
        # This would require connection to a node with mempool access
        # For now, we'll simulate with a placeholder
        while self._running:
            try:
                # Placeholder for mempool monitoring
                # In production, you'd use websocket to a node
                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"Error monitoring pending transactions: {e}")
                await asyncio.sleep(5)

    async def emit_transaction(self, tx_hash: str, tx_data: Dict[str, Any]) -> None:
        """
        Emit a transaction event.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.
        tx_data : dict
            Transaction data.
        """
        message = WebSocketMessage(
            type="transaction",
            data={
                "hash": tx_hash,
                "from": tx_data.get("from"),
                "to": tx_data.get("to"),
                "value": tx_data.get("value"),
                "status": tx_data.get("status", "pending"),
            },
            channel="transactions"
        )
        await self.manager.broadcast(message, channel="transactions")
        logger.info(f"💳 Transaction broadcast: {tx_hash[:10]}...")

    async def emit_wallet_update(self, address: str, balance: Dict[str, Any]) -> None:
        """
        Emit a wallet update event.

        Parameters
        ----------
        address : str
            Wallet address.
        balance : dict
            Balance information.
        """
        message = WebSocketMessage(
            type="wallet_update",
            data={
                "address": address,
                "balance": balance,
            },
            channel=f"wallet_{address[:10]}"
        )
        await self.manager.broadcast(message, channel=f"wallet_{address[:10]}")
        logger.info(f"👛 Wallet update broadcast: {address[:10]}...")


# Singleton instance
_emitter = None


def get_event_emitter() -> BlockchainEventEmitter:
    """Get the blockchain event emitter instance."""
    global _emitter
    if _emitter is None:
        _emitter = BlockchainEventEmitter()
    return _emitter
