"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
web.socketio

Purpose
-------
WebSocket integration for real-time updates.

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0 Enterprise
===============================================================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user

from core.logger import get_logger

logger = get_logger(__name__)

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*")


def init_socketio(app):
    """Initialize SocketIO with the Flask app."""
    socketio.init_app(app, async_mode='eventlet')
    logger.info("SocketIO initialized")
    return socketio


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    logger.info(f"WebSocket client connected: {request.sid}")
    if current_user.is_authenticated:
        emit('message', {'data': f'Welcome {current_user.username}!'}, room=request.sid)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    logger.info(f"WebSocket client disconnected: {request.sid}")


@socketio.on('join')
def handle_join(data):
    """Join a room."""
    room = data.get('room', 'global')
    join_room(room)
    emit('message', {'data': f'Joined room: {room}'}, room=room)


@socketio.on('leave')
def handle_leave(data):
    """Leave a room."""
    room = data.get('room', 'global')
    leave_room(room)
    emit('message', {'data': f'Left room: {room}'}, room=room)


@socketio.on('subscribe_wallet')
def handle_subscribe_wallet(data):
    """Subscribe to wallet updates."""
    address = data.get('address')
    if address:
        room = f'wallet_{address}'
        join_room(room)
        emit('message', {'data': f'Subscribed to wallet: {address}'}, room=room)


@socketio.on('subscribe_block')
def handle_subscribe_block(data):
    """Subscribe to block updates."""
    blockchain = data.get('blockchain', 'ethereum')
    room = f'block_{blockchain}'
    join_room(room)
    emit('message', {'data': f'Subscribed to block updates: {blockchain}'}, room=room)


@socketio.on('message')
def handle_message(data):
    """Handle incoming message."""
    logger.info(f"Message received: {data}")
    emit('response', {'data': f'Message received: {data}'}, broadcast=True)


# ============ Broadcast Functions ============

def broadcast_new_block(blockchain, block_data):
    """Broadcast new block information."""
    room = f'block_{blockchain}'
    socketio.emit('new_block', {
        'blockchain': blockchain,
        'block_data': block_data
    }, room=room)


def broadcast_wallet_update(address, wallet_data):
    """Broadcast wallet update."""
    room = f'wallet_{address}'
    socketio.emit('wallet_update', {
        'address': address,
        'wallet_data': wallet_data
    }, room=room)


def broadcast_transaction(tx_data):
    """Broadcast transaction update."""
    socketio.emit('new_transaction', {
        'transaction': tx_data
    }, broadcast=True)


###############################################################################
# End of File
###############################################################################
