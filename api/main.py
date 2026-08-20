"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
api.main

Purpose
-------
FastAPI REST API entry point for the Universal Blockchain Platform.

Provides:
    - Ethereum inspection endpoints
    - Bitcoin inspection endpoints
    - TRON inspection endpoints
    - Node validation
    - Gas information
    - Real-time WebSocket communication
    - Database persistence helpers

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0.0
===============================================================================
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from fastapi import (
    BackgroundTasks,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
from database.models import (
    WalletInspection,
    ContractInspection,
    TransactionHistory,
)

from ethereum.gas import get_gas_optimizer

from core.websocket.manager import (
    get_connection_manager,
    WebSocketMessage,
)

from core.websocket.events import get_event_emitter


logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

API_TITLE = "Universal Blockchain Platform API"
API_VERSION = "2.0.0"
API_DESCRIPTION = (
    "Enterprise-grade blockchain intelligence API for "
    "Ethereum, Bitcoin, and TRON"
)

DEFAULT_ETHEREUM_CHAIN_ID = 1
DEFAULT_GAS_LIMIT = 21_000
DEFAULT_GAS_URGENCY = "standard"


# =============================================================================
# Database Helpers
# =============================================================================

def get_db_connection():
    """
    Return a SQLAlchemy database connection.

    The caller is responsible for closing the returned connection.
    """
    db_manager = get_db_manager()
    return db_manager.engine.connect()


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


# =============================================================================
# CORS
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this for production deployment.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Controllers
# =============================================================================

logger.info("Initializing UBP API controllers...")

eth_controller = EthereumController()
btc_controller = BitcoinController()
tron_controller = TronController()

logger.info("UBP API controllers initialized successfully.")


# =============================================================================
# WebSocket Services
# =============================================================================

ws_manager = get_connection_manager()
event_emitter = get_event_emitter()


# =============================================================================
# Common Error Handling
# =============================================================================

def _http_error(
    message: str,
    *,
    status_code: int = 400,
    exc: Exception | None = None,
) -> HTTPException:
    """
    Create a consistent HTTPException and log the underlying failure.
    """
    if exc is not None:
        logger.exception(message)
    else:
        logger.error(message)

    return HTTPException(
        status_code=status_code,
        detail=str(exc) if exc is not None else message,
    )


# =============================================================================
# Root & Health Endpoints
# =============================================================================

@app.get("/", response_model=dict)
async def root() -> dict[str, Any]:
    """Return API information and available capabilities."""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "status": "operational",
        "blockchains": [
            "Ethereum",
            "Bitcoin",
            "TRON",
        ],
        "features": [
            "Wallet Inspection",
            "Contract Analysis",
            "Token Information",
            "Block Exploration",
            "Transaction Analysis",
            "Node Validation",
            "Gas Price Optimization",
            "Real-time WebSocket Data",
        ],
        "documentation": "/api/docs",
        "websocket": "ws://localhost:8000/ws/{channel}",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Check API, database, and Ethereum RPC health.

    The endpoint reports:
        healthy:
            Database and Ethereum RPC are available.

        degraded:
            One or more dependencies are unavailable.
    """

    # -------------------------------------------------------------------------
    # Database
    # -------------------------------------------------------------------------
    try:
        db_manager = get_db_manager()

        with db_manager.get_session() as session:
            session.execute(text("SELECT 1"))

        database_status = "healthy"

    except Exception as exc:
        logger.exception("Database health check failed")
        database_status = "unhealthy"

    # -------------------------------------------------------------------------
    # Ethereum RPC
    # -------------------------------------------------------------------------
    try:
        web3 = eth_controller.connection

        if web3.is_connected():
            rpc_status = "healthy"
            chain_id = web3.eth.chain_id
        else:
            rpc_status = "unhealthy"
            chain_id = None

    except Exception:
        logger.exception("Ethereum RPC health check failed")
        rpc_status = "unhealthy"
        chain_id = None

    # -------------------------------------------------------------------------
    # Overall status
    # -------------------------------------------------------------------------
    overall_status = (
        "healthy"
        if database_status == "healthy"
        and rpc_status == "healthy"
        else "degraded"
    )

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        database=database_status,
        blockchain="Ethereum",
        chain_id=chain_id,
    )


# =============================================================================
# Ethereum Endpoints
# =============================================================================

@app.post(
    "/api/ethereum/wallet/inspect",
    response_model=WalletResponse,
)
async def inspect_ethereum_wallet(
    request: AddressRequest,
) -> WalletResponse:
    """Inspect an Ethereum wallet address."""
    try:
        report = eth_controller.wallet_inspector(
            request.address,
        )

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

    except Exception as exc:
        raise _http_error(
            "Ethereum wallet inspection failed",
            exc=exc,
        ) from exc


@app.post(
    "/api/ethereum/contract/inspect",
    response_model=ContractResponse,
)
async def inspect_ethereum_contract(
    request: AddressRequest,
) -> ContractResponse:
    """Inspect an Ethereum contract address."""
    try:
        report = eth_controller.contract_inspector(
            request.address,
        )

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

    except Exception as exc:
        raise _http_error(
            "Ethereum contract inspection failed",
            exc=exc,
        ) from exc


@app.post(
    "/api/ethereum/token/inspect",
    response_model=TokenResponse,
)
async def inspect_ethereum_token(
    request: AddressRequest,
) -> TokenResponse:
    """Inspect an ERC-20 token."""
    try:
        report = eth_controller.token_inspector(
            request.address,
        )

        return TokenResponse(
            address=report.get("address"),
            name=report.get("name", "Unknown"),
            symbol=report.get("symbol", "Unknown"),
            decimals=report.get("decimals", 18),
            total_supply=report.get("total_supply"),
            is_token=report.get("is_token", False),
        )

    except Exception as exc:
        raise _http_error(
            "Ethereum token inspection failed",
            exc=exc,
        ) from exc


@app.post(
    "/api/ethereum/block/explore",
    response_model=BlockResponse,
)
async def explore_ethereum_block(
    request: BlockRequest,
) -> BlockResponse:
    """Explore an Ethereum block."""
    try:
        report = eth_controller.block_explorer(
            request.block_identifier,
        )

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

    except Exception as exc:
        raise _http_error(
            "Ethereum block exploration failed",
            exc=exc,
        ) from exc


@app.post(
    "/api/ethereum/transaction/analyze",
    response_model=TransactionResponse,
)
async def analyze_ethereum_transaction(
    request: TransactionRequest,
) -> TransactionResponse:
    """Analyze an Ethereum transaction."""
    try:
        report = eth_controller.transaction_analyzer(
            request.tx_hash,
        )

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

    except Exception as exc:
        raise _http_error(
            "Ethereum transaction analysis failed",
            exc=exc,
        ) from exc


@app.get(
    "/api/ethereum/gas/price",
    response_model=GasPriceResponse,
)
async def get_ethereum_gas_price() -> GasPriceResponse:
    """Get the current Ethereum gas price."""
    try:
        optimizer = get_gas_optimizer()
        gas_info = optimizer.get_gas_price()

        return GasPriceResponse(
            wei=gas_info.get("wei", 0),
            gwei=gas_info.get("gwei", 0),
            eth=gas_info.get("eth", 0),
        )

    except Exception as exc:
        raise _http_error(
            "Ethereum gas price retrieval failed",
            exc=exc,
        ) from exc


@app.post(
    "/api/ethereum/gas/estimate",
    response_model=GasEstimateResponse,
)
async def estimate_ethereum_gas(
    request: dict[str, Any],
) -> GasEstimateResponse:
    """Estimate Ethereum gas cost."""
    try:
        optimizer = get_gas_optimizer()

        gas_limit = request.get(
            "gas_limit",
            DEFAULT_GAS_LIMIT,
        )

        gas_price_gwei = request.get(
            "gas_price_gwei",
        )

        estimate = optimizer.estimate_gas_cost(
            gas_limit,
            gas_price_gwei,
        )

        return GasEstimateResponse(
            gas_limit=estimate.get("gas_limit", 0),
            gas_price_gwei=estimate.get("gas_price_gwei", 0),
            total_cost_wei=estimate.get("total_cost_wei", 0),
            total_cost_eth=estimate.get("total_cost_eth", 0),
            total_cost_usd=estimate.get("total_cost_usd", 0),
        )

    except Exception as exc:
        raise _http_error(
            "Ethereum gas estimation failed",
            exc=exc,
        ) from exc


@app.get("/api/ethereum/gas/optimal")
async def get_optimal_gas_price(
    urgency: str = DEFAULT_GAS_URGENCY,
) -> Any:
    """Get optimal Ethereum gas price recommendations."""
    try:
        optimizer = get_gas_optimizer()

        return optimizer.get_optimal_gas_price(
            urgency,
        )

    except Exception as exc:
        raise _http_error(
            "Optimal Ethereum gas price retrieval failed",
            exc=exc,
        ) from exc


# =============================================================================
# Node Validation
# =============================================================================

@app.post(
    "/api/node/validate",
    response_model=NodeValidationResponse,
)
async def validate_node(
    request: AddressRequest,
) -> NodeValidationResponse:
    """Validate a blockchain node."""
    try:
        node_url = request.address or None

        report = eth_controller.node_validator(
            node_url,
        )

        return NodeValidationResponse(
            is_connected=report.get(
                "is_connected",
                False,
            ),
            is_syncing=report.get(
                "is_syncing",
                False,
            ),
            node_type=report.get(
                "node_type",
                "Unknown",
            ),
            chain_id=report.get(
                "chain_id",
                0,
            ),
            block_number=report.get(
                "block_number",
                0,
            ),
            peer_count=report.get(
                "peer_count",
                0,
            ),
            response_time_ms=report.get(
                "response_time_ms",
                0,
            ),
            health_status=report.get(
                "health_status",
                "Unknown",
            ),
            issues=report.get(
                "issues",
                [],
            ),
        )

    except Exception as exc:
        raise _http_error(
            "Node validation failed",
            exc=exc,
        ) from exc


@app.post(
    "/api/node/compare",
    response_model=dict,
)
async def compare_nodes(
    request: CompareNodesRequest,
) -> dict[str, Any]:
    """Compare multiple blockchain nodes."""
    try:
        report = eth_controller.compare_nodes(
            request.node_urls,
        )

        return JSONResponse(
            content=report,
        )

    except Exception as exc:
        raise _http_error(
            "Node comparison failed",
            exc=exc,
        ) from exc


# =============================================================================
# Bitcoin Endpoints
# =============================================================================

@app.post(
    "/api/bitcoin/wallet/inspect",
    response_model=dict,
)
async def inspect_bitcoin_wallet(
    request: AddressRequest,
) -> dict[str, Any]:
    """Inspect a Bitcoin wallet address."""
    try:
        report = btc_controller.wallet_inspector(
            request.address,
        )

        return JSONResponse(
            content=report,
        )

    except Exception as exc:
        raise _http_error(
            "Bitcoin wallet inspection failed",
            exc=exc,
        ) from exc


@app.post(
    "/api/bitcoin/block/explore",
    response_model=dict,
)
async def explore_bitcoin_block(
    request: BlockRequest,
) -> dict[str, Any]:
    """Explore a Bitcoin block."""
    try:
        report = btc_controller.block_explorer(
            request.block_identifier,
        )

        return JSONResponse(
            content=report,
        )

    except Exception as exc:
        raise _http_error(
            "Bitcoin block exploration failed",
            exc=exc,
        ) from exc


@app.post(
    "/api/bitcoin/transaction/analyze",
    response_model=dict,
)
async def analyze_bitcoin_transaction(
    request: TransactionRequest,
) -> dict[str, Any]:
    """Analyze a Bitcoin transaction."""
    try:
        report = btc_controller.transaction_analyzer(
            request.tx_hash,
        )

        return JSONResponse(
            content=report,
        )

    except Exception as exc:
        raise _http_error(
            "Bitcoin transaction analysis failed",
            exc=exc,
        ) from exc


# =============================================================================
# TRON Endpoints
# =============================================================================

@app.post(
    "/api/tron/wallet/inspect",
    response_model=dict,
)
async def inspect_tron_wallet(
    request: AddressRequest,
) -> dict[str, Any]:
    """Inspect a TRON wallet address."""
    try:
        report = tron_controller.wallet_inspector(
            request.address,
        )

        return JSONResponse(
            content=report,
        )

    except Exception as exc:
        raise _http_error(
            "TRON wallet inspection failed",
            exc=exc,
        ) from exc


@app.post(
    "/api/tron/contract/inspect",
    response_model=dict,
)
async def inspect_tron_contract(
    request: AddressRequest,
) -> dict[str, Any]:
    """Inspect a TRON contract address."""
    try:
        report = tron_controller.contract_inspector(
            request.address,
        )

        return JSONResponse(
            content=report,
        )

    except Exception as exc:
        raise _http_error(
            "TRON contract inspection failed",
            exc=exc,
        ) from exc


@app.post(
    "/api/tron/token/inspect",
    response_model=dict,
)
async def inspect_tron_token(
    request: AddressRequest,
) -> dict[str, Any]:
    """Inspect a TRC-20 token."""
    try:
        report = tron_controller.token_inspector(
            request.address,
        )

        return JSONResponse(
            content=report,
        )

    except Exception as exc:
        raise _http_error(
            "TRON token inspection failed",
            exc=exc,
        ) from exc


# =============================================================================
# WebSocket Endpoint
# =============================================================================

@app.websocket("/ws/{channel}")
async def websocket_endpoint(
    websocket: WebSocket,
    channel: str = "global",
):
    """
    WebSocket endpoint for real-time blockchain data.

    Supported channels:
        global
        blocks
        transactions
        wallet_{address}

    Supported client messages:
        subscribe
        unsubscribe
        ping
        get_block
        get_wallet
    """

    current_channel = channel

    await ws_manager.connect(
        websocket,
        current_channel,
    )

    logger.info(
        "WebSocket connected to channel: %s",
        current_channel,
    )

    try:
        # ---------------------------------------------------------------------
        # Welcome message
        # ---------------------------------------------------------------------
        await websocket.send_text(
            json.dumps(
                {
                    "type": "welcome",
                    "data": {
                        "channel": current_channel,
                        "message": (
                            f"Connected to "
                            f"{current_channel} channel"
                        ),
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                }
            )
        )

        # ---------------------------------------------------------------------
        # Client message loop
        # ---------------------------------------------------------------------
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "data": "Invalid JSON format",
                        }
                    )
                )
                continue

            if not isinstance(message, dict):
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "data": "WebSocket message must be a JSON object",
                        }
                    )
                )
                continue

            message_type = message.get("type")

            # -----------------------------------------------------------------
            # Subscribe
            # -----------------------------------------------------------------
            if message_type == "subscribe":
                new_channel = message.get(
                    "channel",
                    current_channel,
                )

                await ws_manager.connect(
                    websocket,
                    new_channel,
                )

                current_channel = new_channel

                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "subscribed",
                            "data": {
                                "channel": current_channel,
                            },
                        }
                    )
                )

                logger.info(
                    "WebSocket client subscribed to: %s",
                    current_channel,
                )

            # -----------------------------------------------------------------
            # Unsubscribe
            # -----------------------------------------------------------------
            elif message_type == "unsubscribe":
                old_channel = message.get(
                    "channel",
                    current_channel,
                )

                await ws_manager.disconnect(
                    websocket,
                    old_channel,
                )

                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "unsubscribed",
                            "data": {
                                "channel": old_channel,
                            },
                        }
                    )
                )

                logger.info(
                    "WebSocket client unsubscribed from: %s",
                    old_channel,
                )

            # -----------------------------------------------------------------
            # Ping
            # -----------------------------------------------------------------
            elif message_type == "ping":
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "pong",
                            "data": {
                                "timestamp": (
                                    datetime.utcnow().isoformat()
                                ),
                            },
                        }
                    )
                )

            # -----------------------------------------------------------------
            # Latest block
            # -----------------------------------------------------------------
            elif message_type == "get_block":
                from ethereum.blocks import get_block

                block = get_block("latest")

                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "block",
                            "data": block,
                        }
                    )
                )

            # -----------------------------------------------------------------
            # Wallet information
            # -----------------------------------------------------------------
            elif message_type == "get_wallet":
                address = message.get("address")

                if not address:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "error",
                                "data": "Wallet address is required",
                            }
                        )
                    )
                    continue

                report = eth_controller.wallet_inspector(
                    address,
                )

                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "wallet",
                            "data": report,
                        }
                    )
                )

            # -----------------------------------------------------------------
            # Unknown message
            # -----------------------------------------------------------------
            else:
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "data": (
                                f"Unknown message type: "
                                f"{message_type}"
                            ),
                        }
                    )
                )

    except WebSocketDisconnect:
        logger.info(
            "WebSocket disconnected from channel: %s",
            current_channel,
        )

    except Exception:
        logger.exception(
            "WebSocket error on channel: %s",
            current_channel,
        )

    finally:
        try:
            await ws_manager.disconnect(
                websocket,
                current_channel,
            )
        except Exception:
            logger.exception(
                "Failed to clean up WebSocket connection "
                "for channel: %s",
                current_channel,
            )


# =============================================================================
# Background Database Persistence Helpers
# =============================================================================

def save_wallet_inspection(
    address: str,
    report: dict[str, Any],
    chain_id: int,
) -> None:
    """Persist a wallet inspection result."""
    db = None

    try:
        db = get_db_connection()

        statement = text(
            """
            INSERT INTO wallet_inspections (
                address,
                balance_eth,
                balance_wei,
                nonce,
                is_contract,
                classification,
                chain_id
            )
            VALUES (
                :address,
                :balance_eth,
                :balance_wei,
                :nonce,
                :is_contract,
                :classification,
                :chain_id
            )
            """
        )

        db.execute(
            statement,
            {
                "address": address,
                "balance_eth": report.get(
                    "balance_eth",
                    0,
                ),
                "balance_wei": str(
                    report.get(
                        "balance_wei",
                        0,
                    )
                ),
                "nonce": report.get(
                    "nonce",
                    0,
                ),
                "is_contract": report.get(
                    "is_contract",
                    False,
                ),
                "classification": report.get(
                    "classification",
                    "Unknown",
                ),
                "chain_id": chain_id,
            },
        )

        db.commit()

    except Exception:
        logger.exception(
            "Failed to save wallet inspection for %s",
            address,
        )

    finally:
        if db is not None:
            db.close()


def save_contract_inspection(
    address: str,
    report: dict[str, Any],
    chain_id: int,
) -> None:
    """Persist a contract inspection result."""
    db = None

    try:
        db = get_db_connection()

        metadata = report.get(
            "metadata",
            {},
        )

        statement = text(
            """
            INSERT INTO contract_inspections (
                address,
                contract_type,
                name,
                symbol,
                decimals,
                total_supply,
                bytecode_size,
                owner,
                standard,
                chain_id
            )
            VALUES (
                :address,
                :contract_type,
                :name,
                :symbol,
                :decimals,
                :total_supply,
                :bytecode_size,
                :owner,
                :standard,
                :chain_id
            )
            """
        )

        db.execute(
            statement,
            {
                "address": address,
                "contract_type": report.get(
                    "contract_type",
                    "Unknown",
                ),
                "name": metadata.get("name"),
                "symbol": metadata.get("symbol"),
                "decimals": metadata.get("decimals"),
                "total_supply": str(
                    metadata.get(
                        "total_supply",
                    )
                ),
                "bytecode_size": report.get(
                    "bytecode_size",
                    0,
                ),
                "owner": metadata.get("owner"),
                "standard": metadata.get("standard"),
                "chain_id": chain_id,
            },
        )

        db.commit()

    except Exception:
        logger.exception(
            "Failed to save contract inspection for %s",
            address,
        )

    finally:
        if db is not None:
            db.close()


def save_transaction_history(
    tx_hash: str,
    report: dict[str, Any],
    chain_id: int,
) -> None:
    """Persist transaction analysis history."""
    db = None

    try:
        db = get_db_connection()

        statement = text(
            """
            INSERT INTO transaction_history (
                tx_hash,
                from_address,
                to_address,
                value_eth,
                gas_used,
                gas_price,
                block_number,
                status,
                chain_id
            )
            VALUES (
                :tx_hash,
                :from_address,
                :to_address,
                :value_eth,
                :gas_used,
                :gas_price,
                :block_number,
                :status,
                :chain_id
            )
            ON CONFLICT (tx_hash) DO UPDATE SET
                status = excluded.status,
                updated_at = CURRENT_TIMESTAMP
            """
        )

        db.execute(
            statement,
            {
                "tx_hash": tx_hash,
                "from_address": report.get("from"),
                "to_address": report.get("to"),
                "value_eth": report.get(
                    "value",
                    0,
                ),
                "gas_used": report.get(
                    "gas_used",
                ),
                "gas_price": report.get(
                    "gas_price",
                ),
                "block_number": report.get(
                    "block_number",
                ),
                "status": report.get(
                    "is_success",
                    False,
                ),
                "chain_id": chain_id,
            },
        )

        db.commit()

    except Exception:
        logger.exception(
            "Failed to save transaction history for %s",
            tx_hash,
        )

    finally:
        if db is not None:
            db.close()