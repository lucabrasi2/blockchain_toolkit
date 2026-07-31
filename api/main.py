"""
Universal Blockchain Platform (UBP)

Module:
    FastAPI Main Entry Point

Purpose:
    REST API for the Universal Blockchain Platform.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List, Any
from datetime import datetime
import logging
import json
from sqlalchemy import text

from api.models import (
    AddressRequest,
    BlockRequest,
    TransactionRequest,
    WalletResponse,
    ContractResponse,
    TokenResponse,
    BlockResponse,
    TransactionResponse,
    NodeValidationResponse,
    HealthResponse,
    GasPriceResponse,
    GasEstimateResponse,
    CompareNodesRequest,
)
from controllers.ethereum_controller import EthereumController
from controllers.bitcoin_controller import BitcoinController
from controllers.tron_controller import TronController
from database.database import get_db_manager
from database.models import WalletInspection, ContractInspection, TransactionHistory
from ethereum.gas import get_gas_optimizer
from core.websocket.manager import get_connection_manager, WebSocketMessage
from core.websocket.events import get_event_emitter

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get a raw database connection."""
    db_manager = get_db_manager()
    return db_manager.engine.connect()

# Create FastAPI app
app = FastAPI(
    title="Universal Blockchain Platform API",
    description="Enterprise-grade blockchain intelligence API for Ethereum, Bitcoin, and TRON",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize controllers
eth_controller = EthereumController()
btc_controller = BitcoinController()
tron_controller = TronController()

# WebSocket manager
ws_manager = get_connection_manager()
event_emitter = get_event_emitter()


# ============ Root & Health Endpoints ============

@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "name": "Universal Blockchain Platform API",
        "version": "2.0.0",
        "status": "operational",
        "blockchains": ["Ethereum", "Bitcoin", "TRON"],
        "features": [
            "Wallet Inspection",
            "Contract Analysis",
            "Token Information",
            "Block Exploration",
            "Transaction Analysis",
            "Node Validation",
            "Gas Price Optimization",
            "Real-time WebSocket Data"
        ],
        "documentation": "/api/docs",
        "websocket": "ws://localhost:8000/ws/{channel}",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    # Check database connectivity
    try:
        db_manager = get_db_manager()
        with db_manager.get_session() as session:
            session.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    # Check Ethereum node / RPC connectivity
    try:
        w3 = eth_controller.connection
        if w3.is_connected():
            rpc_status = "healthy"
            chain_id = w3.eth.chain_id
        else:
            rpc_status = "unhealthy"
            chain_id = None
    except Exception:
        rpc_status = "unhealthy"
        chain_id = None

    return HealthResponse(
        status=("healthy" if db_status == "healthy" and rpc_status == "healthy" else "degraded"),
        timestamp=datetime.utcnow().isoformat(),
        database=db_status,
        blockchain="Ethereum",
        chain_id=chain_id or 1,
    )


# ============ Ethereum Endpoints ============

@app.post("/api/ethereum/wallet/inspect", response_model=WalletResponse)
async def inspect_ethereum_wallet(request: AddressRequest, background_tasks: BackgroundTasks):
    """Inspect an Ethereum wallet address."""
    try:
        report = eth_controller.wallet_inspector(request.address)
        return WalletResponse(
            address=report.get("address"),
            balance_eth=report.get("balance_eth", 0),
            balance_wei=report.get("balance_wei", 0),
            nonce=report.get("nonce", 0),
            is_contract=report.get("is_contract", False),
            classification=report.get("classification", "Unknown"),
            transaction_count=report.get("transaction_count", 0),
            token_balances=report.get("token_balances", []),
        )
    except Exception as e:
        logger.error(f"Wallet inspection failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ethereum/contract/inspect", response_model=ContractResponse)
async def inspect_ethereum_contract(request: AddressRequest, background_tasks: BackgroundTasks):
    """Inspect an Ethereum contract address."""
    try:
        report = eth_controller.contract_inspector(request.address)
        metadata = report.get("metadata", {})
        return ContractResponse(
            address=report.get("address"),
            is_contract=report.get("is_contract", False),
            classification=report.get("classification", "Unknown"),
            contract_type=report.get("contract_type", "Unknown"),
            name=metadata.get("name"),
            symbol=metadata.get("symbol"),
            decimals=metadata.get("decimals"),
            total_supply=metadata.get("total_supply"),
            owner=metadata.get("owner"),
            standard=metadata.get("standard"),
            bytecode_size=report.get("bytecode_size", 0),
            balance_eth=report.get("balance_eth", 0),
        )
    except Exception as e:
        logger.error(f"Contract inspection failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ethereum/token/inspect", response_model=TokenResponse)
async def inspect_ethereum_token(request: AddressRequest):
    """Inspect an ERC-20 token."""
    try:
        report = eth_controller.token_inspector(request.address)
        return TokenResponse(
            address=report.get("address"),
            name=report.get("name", "Unknown"),
            symbol=report.get("symbol", "Unknown"),
            decimals=report.get("decimals", 18),
            total_supply=report.get("total_supply"),
            is_token=report.get("is_token", False),
        )
    except Exception as e:
        logger.error(f"Token inspection failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ethereum/block/explore", response_model=BlockResponse)
async def explore_ethereum_block(request: BlockRequest):
    """Explore an Ethereum block."""
    try:
        report = eth_controller.block_explorer(request.block_identifier)
        return BlockResponse(
            number=report.get("number"),
            hash=report.get("hash"),
            parent_hash=report.get("parent_hash"),
            timestamp=report.get("timestamp"),
            miner=report.get("miner"),
            difficulty=report.get("difficulty"),
            gas_used=report.get("gas_used"),
            gas_limit=report.get("gas_limit"),
            transaction_count=report.get("transaction_count", 0),
            transactions=report.get("transactions", []),
        )
    except Exception as e:
        logger.error(f"Block exploration failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ethereum/transaction/analyze", response_model=TransactionResponse)
async def analyze_ethereum_transaction(request: TransactionRequest, background_tasks: BackgroundTasks):
    """Analyze an Ethereum transaction."""
    try:
        report = eth_controller.transaction_analyzer(request.tx_hash)
        return TransactionResponse(
            hash=report.get("hash"),
            block_number=report.get("block_number"),
            from_address=report.get("from"),
            to_address=report.get("to"),
            value_eth=report.get("value", 0),
            gas_used=report.get("gas_used"),
            gas_price=report.get("gas_price"),
            status=report.get("is_success", False),
            logs=report.get("logs", []),
        )
    except Exception as e:
        logger.error(f"Transaction analysis failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/ethereum/gas/price", response_model=GasPriceResponse)
async def get_ethereum_gas_price():
    """Get current Ethereum gas price."""
    try:
        optimizer = get_gas_optimizer()
        gas_info = optimizer.get_gas_price()
        return GasPriceResponse(
            wei=gas_info.get("wei", 0),
            gwei=gas_info.get("gwei", 0),
            eth=gas_info.get("eth", 0),
        )
    except Exception as e:
        logger.error(f"Gas price fetch failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ethereum/gas/estimate", response_model=GasEstimateResponse)
async def estimate_ethereum_gas(request: dict):
    """Estimate Ethereum gas cost."""
    try:
        optimizer = get_gas_optimizer()
        gas_limit = request.get("gas_limit", 21000)
        gas_price_gwei = request.get("gas_price_gwei")
        estimate = optimizer.estimate_gas_cost(gas_limit, gas_price_gwei)
        return GasEstimateResponse(
            gas_limit=estimate.get("gas_limit", 0),
            gas_price_gwei=estimate.get("gas_price_gwei", 0),
            total_cost_wei=estimate.get("total_cost_wei", 0),
            total_cost_eth=estimate.get("total_cost_eth", 0),
            total_cost_usd=estimate.get("total_cost_usd", 0),
        )
    except Exception as e:
        logger.error(f"Gas estimate failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/ethereum/gas/optimal")
async def get_optimal_gas_price(urgency: str = "standard"):
    """Get optimal gas price recommendations."""
    try:
        optimizer = get_gas_optimizer()
        return optimizer.get_optimal_gas_price(urgency)
    except Exception as e:
        logger.error(f"Optimal gas price fetch failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============ Node Validation ============

@app.post("/api/node/validate", response_model=NodeValidationResponse)
async def validate_node(request: AddressRequest):
    """Validate a blockchain node."""
    try:
        report = eth_controller.node_validator(request.address if request.address else None)
        return NodeValidationResponse(
            is_connected=report.get("is_connected", False),
            is_syncing=report.get("is_syncing", False),
            node_type=report.get("node_type", "Unknown"),
            chain_id=report.get("chain_id", 0),
            block_number=report.get("block_number", 0),
            peer_count=report.get("peer_count", 0),
            response_time_ms=report.get("response_time_ms", 0),
            health_status=report.get("health_status", "Unknown"),
            issues=report.get("issues", []),
        )
    except Exception as e:
        logger.error(f"Node validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/node/compare", response_model=dict)
async def compare_nodes(request: CompareNodesRequest):
    """Compare multiple blockchain nodes."""
    try:
        report = eth_controller.compare_nodes(request.node_urls)
        return JSONResponse(content=report)
    except Exception as e:
        logger.error(f"Node comparison failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============ Bitcoin Endpoints ============

@app.post("/api/bitcoin/wallet/inspect", response_model=dict)
async def inspect_bitcoin_wallet(request: AddressRequest):
    """Inspect a Bitcoin wallet address."""
    try:
        report = btc_controller.wallet_inspector(request.address)
        return JSONResponse(content=report)
    except Exception as e:
        logger.error(f"Bitcoin wallet inspection failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/bitcoin/block/explore", response_model=dict)
async def explore_bitcoin_block(request: BlockRequest):
    """Explore a Bitcoin block."""
    try:
        report = btc_controller.block_explorer(request.block_identifier)
        return JSONResponse(content=report)
    except Exception as e:
        logger.error(f"Bitcoin block exploration failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/bitcoin/transaction/analyze", response_model=dict)
async def analyze_bitcoin_transaction(request: TransactionRequest):
    """Analyze a Bitcoin transaction."""
    try:
        report = btc_controller.transaction_analyzer(request.tx_hash)
        return JSONResponse(content=report)
    except Exception as e:
        logger.error(f"Bitcoin transaction analysis failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============ TRON Endpoints ============

@app.post("/api/tron/wallet/inspect", response_model=dict)
async def inspect_tron_wallet(request: AddressRequest):
    """Inspect a TRON wallet address."""
    try:
        report = tron_controller.wallet_inspector(request.address)
        return JSONResponse(content=report)
    except Exception as e:
        logger.error(f"TRON wallet inspection failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/tron/contract/inspect", response_model=dict)
async def inspect_tron_contract(request: AddressRequest):
    """Inspect a TRON contract address."""
    try:
        report = tron_controller.contract_inspector(request.address)
        return JSONResponse(content=report)
    except Exception as e:
        logger.error(f"TRON contract inspection failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/tron/token/inspect", response_model=dict)
async def inspect_tron_token(request: AddressRequest):
    """Inspect a TRC-20 token."""
    try:
        report = tron_controller.token_inspector(request.address)
        return JSONResponse(content=report)
    except Exception as e:
        logger.error(f"TRON token inspection failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============ WebSocket Endpoint ============

@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str = "global"):
    """
    WebSocket endpoint for real-time blockchain data.
    
    Channels:
    - global: All events
    - blocks: New block notifications
    - transactions: Transaction updates
    - wallet_{address}: Wallet-specific updates
    """
    await ws_manager.connect(websocket, channel)
    logger.info(f"🔌 WebSocket connected to channel: {channel}")
    
    try:
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "welcome",
            "data": {
                "channel": channel,
                "message": f"Connected to {channel} channel",
                "timestamp": datetime.utcnow().isoformat()
            }
        }))
        
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                if msg_type == "subscribe":
                    new_channel = message.get("channel", channel)
                    await ws_manager.connect(websocket, new_channel)
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "data": {"channel": new_channel}
                    }))
                    logger.info(f"📡 Client subscribed to: {new_channel}")
                
                elif msg_type == "unsubscribe":
                    old_channel = message.get("channel", channel)
                    await ws_manager.disconnect(websocket, old_channel)
                    await websocket.send_text(json.dumps({
                        "type": "unsubscribed",
                        "data": {"channel": old_channel}
                    }))
                    logger.info(f"📡 Client unsubscribed from: {old_channel}")
                
                elif msg_type == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "data": {"timestamp": datetime.utcnow().isoformat()}
                    }))
                
                elif msg_type == "get_block":
                    # Client requesting latest block
                    from ethereum.blocks import get_block
                    block = get_block("latest")
                    await websocket.send_text(json.dumps({
                        "type": "block",
                        "data": block
                    }))
                
                elif msg_type == "get_wallet":
                    # Client requesting wallet info
                    address = message.get("address")
                    if address:
                        report = eth_controller.wallet_inspector(address)
                        await websocket.send_text(json.dumps({
                            "type": "wallet",
                            "data": report
                        }))
                
                else:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "data": f"Unknown message type: {msg_type}"
                    }))
                    
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": "Invalid JSON format"
                }))
                
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, channel)
        logger.info(f"🔌 WebSocket disconnected from channel: {channel}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await ws_manager.disconnect(websocket, channel)


# ============ Background Tasks ============

def save_wallet_inspection(address: str, report: dict, chain_id: int):
    """Save wallet inspection to database."""
    try:
        db = get_db_connection()
        db.execute(
            """
            INSERT INTO wallet_inspections (
                address, balance_eth, balance_wei, nonce,
                is_contract, classification, chain_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                address,
                report.get("balance_eth", 0),
                str(report.get("balance_wei", 0)),
                report.get("nonce", 0),
                report.get("is_contract", False),
                report.get("classification", "Unknown"),
                chain_id,
            ),
        )
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save wallet inspection: {e}")


def save_contract_inspection(address: str, report: dict, chain_id: int):
    """Save contract inspection to database."""
    try:
        db = get_db_connection()
        metadata = report.get("metadata", {})
        db.execute(
            """
            INSERT INTO contract_inspections (
                address, contract_type, name, symbol, decimals,
                total_supply, bytecode_size, owner, standard, chain_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                address,
                report.get("contract_type", "Unknown"),
                metadata.get("name"),
                metadata.get("symbol"),
                metadata.get("decimals"),
                str(metadata.get("total_supply")),
                report.get("bytecode_size", 0),
                metadata.get("owner"),
                metadata.get("standard"),
                chain_id,
            ),
        )
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save contract inspection: {e}")


def save_transaction_history(tx_hash: str, report: dict, chain_id: int):
    """Save transaction to history."""
    try:
        db = get_db_connection()
        db.execute(
            """
            INSERT INTO transaction_history (
                tx_hash, from_address, to_address, value_eth,
                gas_used, gas_price, block_number, status, chain_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (tx_hash) DO UPDATE SET
                status = EXCLUDED.status,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                tx_hash,
                report.get("from"),
                report.get("to"),
                report.get("value", 0),
                report.get("gas_used"),
                report.get("gas_price"),
                report.get("block_number"),
                report.get("is_success", False),
                chain_id,
            ),
        )
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save transaction: {e}")
