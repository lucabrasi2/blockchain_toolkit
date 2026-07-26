"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
web.ws

Purpose
-------
WebSocket integration for real-time blockchain updates.

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
from flask import request
from flask_login import current_user
import threading
import time
from datetime import datetime

from core.logger import get_logger

logger = get_logger(__name__)

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')


def init_socketio(app):
    """Initialize SocketIO with the Flask app."""
    socketio.init_app(app, async_mode='threading')
    logger.info("SocketIO initialized")
    return socketio


# ============ WebSocket Event Handlers ============

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    logger.info(f"WebSocket client connected: {request.sid}")
    if current_user.is_authenticated:
        emit('message', {
            'type': 'connection',
            'data': f'Welcome {current_user.username}!',
            'timestamp': datetime.utcnow().isoformat()
        }, room=request.sid)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    logger.info(f"WebSocket client disconnected: {request.sid}")


@socketio.on('join')
def handle_join(data):
    """Join a room for specific updates."""
    room = data.get('room', 'global')
    join_room(room)
    emit('message', {
        'type': 'joined',
        'data': f'Joined room: {room}',
        'room': room,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room)
    logger.info(f"Client {request.sid} joined room: {room}")


@socketio.on('leave')
def handle_leave(data):
    """Leave a room."""
    room = data.get('room', 'global')
    leave_room(room)
    emit('message', {
        'type': 'left',
        'data': f'Left room: {room}',
        'room': room,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room)
    logger.info(f"Client {request.sid} left room: {room}")


@socketio.on('subscribe_wallet')
def handle_subscribe_wallet(data):
    """Subscribe to wallet updates for a specific address."""
    address = data.get('address')
    if address:
        room = f'wallet_{address}'
        join_room(room)
        emit('message', {
            'type': 'subscribed_wallet',
            'data': f'Subscribed to wallet: {address}',
            'address': address,
            'room': room,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room)
        logger.info(f"Client {request.sid} subscribed to wallet: {address}")


@socketio.on('subscribe_block')
def handle_subscribe_block(data):
    """Subscribe to block updates for a specific blockchain."""
    blockchain = data.get('blockchain', 'ethereum')
    room = f'block_{blockchain}'
    join_room(room)
    emit('message', {
        'type': 'subscribed_block',
        'data': f'Subscribed to block updates: {blockchain}',
        'blockchain': blockchain,
        'room': room,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room)
    logger.info(f"Client {request.sid} subscribed to block updates: {blockchain}")


@socketio.on('subscribe_transaction')
def handle_subscribe_transaction(data):
    """Subscribe to transaction updates."""
    blockchain = data.get('blockchain', 'ethereum')
    room = f'transaction_{blockchain}'
    join_room(room)
    emit('message', {
        'type': 'subscribed_transaction',
        'data': f'Subscribed to transaction updates: {blockchain}',
        'blockchain': blockchain,
        'room': room,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room)
    logger.info(f"Client {request.sid} subscribed to transaction updates: {blockchain}")


@socketio.on('get_block')
def handle_get_block(data):
    """Get current block information."""
    blockchain = data.get('blockchain', 'ethereum')
    
    try:
        if blockchain == 'ethereum':
            from ethereum.blocks import get_latest_block
            block = get_latest_block()
            emit('block_data', {
                'blockchain': blockchain,
                'data': block,
                'timestamp': datetime.utcnow().isoformat()
            }, room=request.sid)
        elif blockchain == 'bitcoin':
            from bitcoin.blocks import get_latest_block
            block = get_latest_block()
            emit('block_data', {
                'blockchain': blockchain,
                'data': block,
                'timestamp': datetime.utcnow().isoformat()
            }, room=request.sid)
        elif blockchain == 'tron':
            from tron.blocks import get_latest_block_number, get_block
            block_num = get_latest_block_number()
            block = get_block(block_num)
            emit('block_data', {
                'blockchain': blockchain,
                'data': block,
                'timestamp': datetime.utcnow().isoformat()
            }, room=request.sid)
    except Exception as e:
        emit('error', {
            'message': f'Error fetching block: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }, room=request.sid)


@socketio.on('get_wallet')
def handle_get_wallet(data):
    """Get wallet information."""
    address = data.get('address')
    blockchain = data.get('blockchain', 'ethereum')
    
    if not address:
        emit('error', {
            'message': 'Address required',
            'timestamp': datetime.utcnow().isoformat()
        }, room=request.sid)
        return
    
    try:
        if blockchain == 'ethereum':
            from controllers.ethereum_controller import EthereumController
            controller = EthereumController()
            report = controller.wallet_inspector(address)
            emit('wallet_data', {
                'blockchain': blockchain,
                'address': address,
                'data': report,
                'timestamp': datetime.utcnow().isoformat()
            }, room=request.sid)
        elif blockchain == 'bitcoin':
            from controllers.bitcoin_controller import BitcoinController
            controller = BitcoinController()
            report = controller.wallet_inspector(address)
            emit('wallet_data', {
                'blockchain': blockchain,
                'address': address,
                'data': report,
                'timestamp': datetime.utcnow().isoformat()
            }, room=request.sid)
        elif blockchain == 'tron':
            from controllers.tron_controller import TronController
            controller = TronController()
            report = controller.wallet_inspector(address)
            emit('wallet_data', {
                'blockchain': blockchain,
                'address': address,
                'data': report,
                'timestamp': datetime.utcnow().isoformat()
            }, room=request.sid)
    except Exception as e:
        emit('error', {
            'message': f'Error fetching wallet: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }, room=request.sid)


# ============ Background Monitoring Threads ============

_monitoring_threads = {}
_monitoring_active = False


def start_monitoring():
    """Start background monitoring threads."""
    global _monitoring_active
    if _monitoring_active:
        return
    
    _monitoring_active = True
    logger.info("Starting WebSocket monitoring threads")
    
    thread = threading.Thread(target=_monitor_blocks, daemon=True)
    thread.start()
    _monitoring_threads['blocks'] = thread


def stop_monitoring():
    """Stop background monitoring threads."""
    global _monitoring_active
    _monitoring_active = False
    logger.info("Stopping WebSocket monitoring threads")


def _monitor_blocks():
    """Monitor new blocks and broadcast updates."""
    last_blocks = {
        'ethereum': 0,
        'bitcoin': 0,
        'tron': 0,
    }
    
    while _monitoring_active:
        try:
            # Check Ethereum
            try:
                from ethereum.blocks import get_latest_block
                block = get_latest_block()
                if block and block.get('number') and block.get('number') > last_blocks['ethereum']:
                    last_blocks['ethereum'] = block.get('number')
                    socketio.emit('new_block', {
                        'blockchain': 'ethereum',
                        'block_number': block.get('number'),
                        'hash': block.get('hash'),
                        'transaction_count': block.get('transaction_count', 0),
                        'timestamp': datetime.utcnow().isoformat()
                    }, room='block_ethereum')
                    logger.info(f"New Ethereum block: {block.get('number')}")
            except Exception as e:
                logger.debug(f"Ethereum block monitoring error: {e}")
            
            # Check Bitcoin
            try:
                from bitcoin.blocks import get_latest_block
                block = get_latest_block()
                if block and block.get('number') and block.get('number') > last_blocks['bitcoin']:
                    last_blocks['bitcoin'] = block.get('number')
                    socketio.emit('new_block', {
                        'blockchain': 'bitcoin',
                        'block_number': block.get('number'),
                        'hash': block.get('hash'),
                        'transaction_count': block.get('transaction_count', 0),
                        'timestamp': datetime.utcnow().isoformat()
                    }, room='block_bitcoin')
                    logger.info(f"New Bitcoin block: {block.get('number')}")
            except Exception as e:
                logger.debug(f"Bitcoin block monitoring error: {e}")
            
            # Check TRON
            try:
                from tron.blocks import get_latest_block_number, get_block
                block_num = get_latest_block_number()
                if block_num > last_blocks['tron']:
                    last_blocks['tron'] = block_num
                    block = get_block(block_num)
                    socketio.emit('new_block', {
                        'blockchain': 'tron',
                        'block_number': block_num,
                        'hash': block.get('hash'),
                        'transaction_count': block.get('transaction_count', 0),
                        'timestamp': datetime.utcnow().isoformat()
                    }, room='block_tron')
                    logger.info(f"New TRON block: {block_num}")
            except Exception as e:
                logger.debug(f"TRON block monitoring error: {e}")
            
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"Block monitoring error: {e}")
            time.sleep(10)


# ============ Broadcast Functions ============

def broadcast_new_block(blockchain, block_data):
    """Broadcast new block information."""
    socketio.emit('new_block', {
        'blockchain': blockchain,
        'block_data': block_data,
        'timestamp': datetime.utcnow().isoformat()
    }, room=f'block_{blockchain}')


def broadcast_wallet_update(address, wallet_data):
    """Broadcast wallet update."""
    socketio.emit('wallet_update', {
        'address': address,
        'wallet_data': wallet_data,
        'timestamp': datetime.utcnow().isoformat()
    }, room=f'wallet_{address}')


def broadcast_transaction(blockchain, tx_data):
    """Broadcast transaction update."""
    socketio.emit('new_transaction', {
        'blockchain': blockchain,
        'transaction': tx_data,
        'timestamp': datetime.utcnow().isoformat()
    }, room=f'transaction_{blockchain}')


# Start monitoring when module is imported
start_monitoring()


###############################################################################
# End of File
###############################################################################