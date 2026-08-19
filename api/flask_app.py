"""
Universal Blockchain Platform (UBP)
Flask REST API

Provides HTTP endpoints for interacting with:
- Ethereum
- Bitcoin
- TRON
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple

# ============================================================================
# Project Path
# ============================================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================================
# Flask
# ============================================================================

from flask import Flask, jsonify, request
from flask_cors import CORS


# ============================================================================
# UBP Controllers
# ============================================================================

from controllers.ethereum_controller import EthereumController
from controllers.bitcoin_controller import BitcoinController
from controllers.tron_controller import TronController

from ethereum.gas import get_gas_optimizer

from core.logger import get_logger


# ============================================================================
# Constants
# ============================================================================

API_VERSION = "2.0.0"

API_NAME = "Universal Blockchain Platform API"

SUPPORTED_BLOCKCHAINS = (
    "Ethereum",
    "Bitcoin",
    "TRON",
)

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000


# ============================================================================
# Logger
# ============================================================================

logger = get_logger(__name__)


# ============================================================================
# Controller Initialization
# ============================================================================

logger.info("Initializing controllers for Flask API...")

eth_controller = EthereumController()
btc_controller = BitcoinController()
tron_controller = TronController()

logger.info("Flask API controllers initialized successfully.")


# ============================================================================
# Flask Application
# ============================================================================

app = Flask(__name__)

CORS(app)


# ============================================================================
# Response Helpers
# ============================================================================

def error_response(
    message: str,
    status_code: int = 400,
    *,
    error: Optional[str] = None,
):
    """
    Return a consistent JSON error response.

    Parameters
    ----------
    message:
        Human-readable error message.

    status_code:
        HTTP response status code.

    error:
        Optional machine-readable error identifier.
    """
    payload: Dict[str, Any] = {
        "error": error or message,
        "message": message,
    }

    return jsonify(payload), status_code


def success_response(
    payload: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
):
    """
    Return a JSON success response.
    """
    return jsonify(payload or {}), status_code


# ============================================================================
# Request Helpers
# ============================================================================

def get_json_body() -> Tuple[
    Optional[Dict[str, Any]],
    Optional[Any],
]:
    """
    Safely retrieve a JSON object from the request body.

    Returns
    -------
    tuple
        A tuple containing:

        (data, None)
            when parsing succeeds.

        (None, error_response)
            when the request is invalid.
    """
    if not request.is_json:
        return None, error_response(
            "Request body must contain JSON data.",
            400,
        )

    try:
        data = request.get_json(silent=True)

    except Exception as exc:
        logger.warning(
            "Failed to parse JSON request: %s",
            exc,
        )

        return None, error_response(
            "Invalid JSON request body.",
            400,
        )

    if not isinstance(data, dict):
        return None, error_response(
            "Request body must be a JSON object.",
            400,
        )

    return data, None


def get_required_field(
    data: Dict[str, Any],
    field_name: str,
    display_name: Optional[str] = None,
) -> Tuple[
    Optional[Any],
    Optional[Any],
]:
    """
    Retrieve a required field from a request payload.
    """
    value = data.get(field_name)

    label = (
        display_name
        or field_name.replace("_", " ").title()
    )

    if value is None:
        return None, error_response(
            f"{label} required",
            400,
        )

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return None, error_response(
                f"{label} required",
                400,
            )

    return value, None


def extract_address() -> Tuple[
    Optional[str],
    Optional[Any],
]:
    """
    Extract an address from the current JSON request.
    """
    data, error = get_json_body()

    if error is not None:
        return None, error

    address, error = get_required_field(
        data,
        "address",
        "Address",
    )

    if error is not None:
        return None, error

    return str(address), None


def extract_block_identifier() -> Tuple[
    Optional[Any],
    Optional[Any],
]:
    """
    Extract a block identifier from the current JSON request.
    """
    data, error = get_json_body()

    if error is not None:
        return None, error

    return get_required_field(
        data,
        "block_identifier",
        "Block identifier",
    )


def extract_transaction_hash() -> Tuple[
    Optional[str],
    Optional[Any],
]:
    """
    Extract a transaction hash from the current JSON request.
    """
    data, error = get_json_body()

    if error is not None:
        return None, error

    tx_hash, error = get_required_field(
        data,
        "tx_hash",
        "Transaction hash",
    )

    if error is not None:
        return None, error

    return str(tx_hash), None


# ============================================================================
# API Route Error Handling
# ============================================================================

def api_route(operation: str) -> Callable:
    """
    Decorate an API endpoint with consistent exception handling.

    Existing endpoint behavior is preserved while removing repetitive
    try/except blocks from individual routes.
    """

    def decorator(view_func: Callable) -> Callable:

        @wraps(view_func)
        def wrapped(*args, **kwargs):
            try:
                return view_func(
                    *args,
                    **kwargs,
                )

            except ValueError as exc:
                logger.warning(
                    "API validation error - %s: %s",
                    operation,
                    exc,
                )

                return error_response(
                    str(exc),
                    400,
                )

            except Exception as exc:
                logger.exception(
                    "API Error - %s",
                    operation,
                )

                return error_response(
                    str(exc),
                    400,
                )

        return wrapped

    return decorator


# ============================================================================
# API Documentation
# ============================================================================

def get_endpoint_documentation() -> Dict[str, Any]:
    """
    Return the API endpoint documentation.

    This contains only the endpoints exposed by the original API.
    """
    return {
        "ethereum": {
            "wallet": "/api/ethereum/wallet/inspect",
            "contract": "/api/ethereum/contract/inspect",
            "token": "/api/ethereum/token/inspect",
            "block": "/api/ethereum/block/explore",
            "transaction": "/api/ethereum/transaction/analyze",
            "gas": "/api/ethereum/gas/price",
        },
        "bitcoin": {
            "wallet": "/api/bitcoin/wallet/inspect",
            "block": "/api/bitcoin/block/explore",
            "transaction": "/api/bitcoin/transaction/analyze",
        },
        "tron": {
            "wallet": "/api/tron/wallet/inspect",
            "contract": "/api/tron/contract/inspect",
            "token": "/api/tron/token/inspect",
        },
    }


# ============================================================================
# Root Endpoint
# ============================================================================

@app.route("/", methods=["GET"])
def root():
    """
    Return general API information.
    """
    return success_response({
        "name": API_NAME,
        "version": API_VERSION,
        "status": "operational",
        "blockchains": list(
            SUPPORTED_BLOCKCHAINS
        ),
        "endpoints": get_endpoint_documentation(),
        "documentation": "/api/docs",
        "health": "/health",
    })


# ============================================================================
# Health Check
# ============================================================================

@app.route("/health", methods=["GET"])
def health_check():
    """
    Return Ethereum connectivity and basic chain information.
    """
    connected = False
    chain_id = None
    block_number = None

    try:
        connection = eth_controller.connection

        connected = bool(
            connection.is_connected()
        )

        if connected:
            chain_id = connection.eth.chain_id
            block_number = connection.eth.block_number

    except Exception as exc:
        logger.warning(
            "Health check error: %s",
            exc,
        )

    return jsonify({
        "status": (
            "healthy"
            if connected
            else "degraded"
        ),
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "blockchain": "Ethereum",
        "chain_id": chain_id,
        "block_number": block_number,
        "connected": connected,
    })


# ============================================================================
# API Documentation Endpoint
# ============================================================================

@app.route("/api/docs", methods=["GET"])
def api_docs():
    """
    Return API endpoint documentation.
    """
    return success_response({
        "title": API_NAME,
        "version": API_VERSION,
        "description": (
            "Enterprise-grade blockchain intelligence API"
        ),
        "endpoints": {
            "GET /":
                "API information",

            "GET /health":
                "Health check",

            "GET /api/docs":
                "This documentation",

            "GET /api/ethereum/gas/price":
                "Get current Ethereum gas price",

            "POST /api/ethereum/gas/estimate":
                "Estimate Ethereum gas cost",

            "GET /api/ethereum/gas/optimal":
                "Get optimal Ethereum gas price",

            "POST /api/ethereum/wallet/inspect":
                "Inspect Ethereum wallet",

            "POST /api/ethereum/contract/inspect":
                "Inspect Ethereum contract",

            "POST /api/ethereum/token/inspect":
                "Inspect ERC-20 token",

            "POST /api/ethereum/block/explore":
                "Explore Ethereum block",

            "POST /api/ethereum/transaction/analyze":
                "Analyze Ethereum transaction",

            "POST /api/bitcoin/wallet/inspect":
                "Inspect Bitcoin wallet",

            "POST /api/bitcoin/block/explore":
                "Explore Bitcoin block",

            "POST /api/bitcoin/transaction/analyze":
                "Analyze Bitcoin transaction",

            "POST /api/tron/wallet/inspect":
                "Inspect TRON wallet",

            "POST /api/tron/contract/inspect":
                "Inspect TRON contract",

            "POST /api/tron/token/inspect":
                "Inspect TRC-20 token",

            "POST /api/node/validate":
                "Validate blockchain node",
        },
    })


# ============================================================================
# Global Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """
    Handle unknown routes.
    """
    return jsonify({
        "error": "Endpoint not found",
        "message": (
            "Please check the API documentation "
            "at /api/docs"
        ),
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """
    Handle unexpected Flask application errors.
    """
    logger.error(
        "Internal server error: %s",
        error,
    )

    return jsonify({
        "error": "Internal server error",
        "message": (
            "An unexpected error occurred"
        ),
    }), 500


# ============================================================================
# Ethereum Wallet Endpoint
# ============================================================================

@app.route(
    "/api/ethereum/wallet/inspect",
    methods=["POST"],
)
@api_route("Ethereum wallet inspection")
def inspect_ethereum_wallet():
    """
    Inspect an Ethereum wallet address.

    Request body:
        {
            "address": "0x..."
        }
    """
    address, error = extract_address()

    if error is not None:
        return error

    logger.info(
        "API: Inspecting Ethereum wallet: %s",
        address,
    )

    report = eth_controller.wallet_inspector(
        address
    )

    return jsonify(report)


# ============================================================================
# Ethereum Contract Endpoint
# ============================================================================

@app.route(
    "/api/ethereum/contract/inspect",
    methods=["POST"],
)
@api_route("Ethereum contract inspection")
def inspect_ethereum_contract():
    """
    Inspect an Ethereum contract address.

    Request body:
        {
            "address": "0x..."
        }
    """
    address, error = extract_address()

    if error is not None:
        return error

    logger.info(
        "API: Inspecting Ethereum contract: %s",
        address,
    )

    report = eth_controller.contract_inspector(
        address
    )

    return jsonify(report)


# ============================================================================
# Ethereum Token Endpoint
# ============================================================================

@app.route(
    "/api/ethereum/token/inspect",
    methods=["POST"],
)
@api_route("Ethereum token inspection")
def inspect_ethereum_token():
    """
    Inspect an ERC-20 token.

    Request body:
        {
            "address": "0x..."
        }
    """
    address, error = extract_address()

    if error is not None:
        return error

    logger.info(
        "API: Inspecting Ethereum token: %s",
        address,
    )

    report = eth_controller.token_inspector(
        address
    )

    return jsonify(report)
# ============================================================================
# Ethereum Block Endpoint
# ============================================================================

@app.route(
    "/api/ethereum/block/explore",
    methods=["POST"],
)
@api_route("Ethereum block exploration")
def explore_ethereum_block():
    """
    Explore an Ethereum block.

    Request body:
        {
            "block_identifier": "latest"
        }
    """
    block_identifier, error = extract_block_identifier()

    if error is not None:
        return error

    logger.info(
        "API: Exploring Ethereum block: %s",
        block_identifier,
    )

    report = eth_controller.block_explorer(
        block_identifier
    )

    return jsonify(report)


# ============================================================================
# Ethereum Transaction Endpoint
# ============================================================================

@app.route(
    "/api/ethereum/transaction/analyze",
    methods=["POST"],
)
@api_route("Ethereum transaction analysis")
def analyze_ethereum_transaction():
    """
    Analyze an Ethereum transaction.

    Request body:
        {
            "tx_hash": "0x..."
        }
    """
    tx_hash, error = extract_transaction_hash()

    if error is not None:
        return error

    logger.info(
        "API: Analyzing Ethereum transaction: %s",
        tx_hash,
    )

    report = eth_controller.transaction_analyzer(
        tx_hash
    )

    return jsonify(report)


# ============================================================================
# Ethereum Gas Price
# ============================================================================

@app.route(
    "/api/ethereum/gas/price",
    methods=["GET"],
)
@api_route("Ethereum gas price")
def get_ethereum_gas_price():
    """
    Get the current Ethereum gas price.
    """
    logger.info(
        "API: Getting Ethereum gas price"
    )

    optimizer = get_gas_optimizer()

    gas_price = optimizer.get_gas_price()

    if isinstance(gas_price, dict):
        return jsonify(gas_price)

    return jsonify({
        "gas_price": gas_price,
    })


# ============================================================================
# Ethereum Gas Estimation
# ============================================================================

@app.route(
    "/api/ethereum/gas/estimate",
    methods=["POST"],
)
@api_route("Ethereum gas estimation")
def estimate_ethereum_gas():
    """
    Estimate Ethereum gas cost.

    Request body:
        {
            "gas_limit": 21000,
            "gas_price_gwei": 20
        }
    """
    data, error = get_json_body()

    if error is not None:
        return error

    gas_limit = data.get(
        "gas_limit",
        21000,
    )

    gas_price_gwei = data.get(
        "gas_price_gwei"
    )

    logger.info(
        "API: Estimating Ethereum gas - "
        "gas_limit=%s, gas_price_gwei=%s",
        gas_limit,
        gas_price_gwei,
    )

    optimizer = get_gas_optimizer()

    estimate = optimizer.estimate_gas_cost(
        gas_limit,
        gas_price_gwei,
    )

    return jsonify(estimate)


# ============================================================================
# Ethereum Optimal Gas Price
# ============================================================================

@app.route(
    "/api/ethereum/gas/optimal",
    methods=["GET"],
)
@api_route("Ethereum optimal gas price")
def get_optimal_gas_price():
    """
    Get an optimal Ethereum gas price recommendation.

    Query parameters:
        urgency:
            slow
            standard
            fast
            instant
    """
    urgency = request.args.get(
        "urgency",
        "standard",
    )

    logger.info(
        "API: Getting optimal gas price - "
        "urgency=%s",
        urgency,
    )

    optimizer = get_gas_optimizer()

    recommendations = optimizer.get_optimal_gas_price(
        urgency
    )

    return jsonify(recommendations)


# ============================================================================
# Bitcoin Wallet Endpoint
# ============================================================================

@app.route(
    "/api/bitcoin/wallet/inspect",
    methods=["POST"],
)
@api_route("Bitcoin wallet inspection")
def inspect_bitcoin_wallet():
    """
    Inspect a Bitcoin wallet address.

    Request body:
        {
            "address": "bc1..."
        }
    """
    address, error = extract_address()

    if error is not None:
        return error

    logger.info(
        "API: Inspecting Bitcoin wallet: %s",
        address,
    )

    report = btc_controller.wallet_inspector(
        address
    )

    return jsonify(report)


# ============================================================================
# Bitcoin Block Endpoint
# ============================================================================

@app.route(
    "/api/bitcoin/block/explore",
    methods=["POST"],
)
@api_route("Bitcoin block exploration")
def explore_bitcoin_block():
    """
    Explore a Bitcoin block.

    Request body:
        {
            "block_identifier": "latest"
        }
    """
    block_identifier, error = extract_block_identifier()

    if error is not None:
        return error

    logger.info(
        "API: Exploring Bitcoin block: %s",
        block_identifier,
    )

    report = btc_controller.block_explorer(
        block_identifier
    )

    return jsonify(report)


# ============================================================================
# Bitcoin Transaction Endpoint
# ============================================================================

@app.route(
    "/api/bitcoin/transaction/analyze",
    methods=["POST"],
)
@api_route("Bitcoin transaction analysis")
def analyze_bitcoin_transaction():
    """
    Analyze a Bitcoin transaction.

    Request body:
        {
            "tx_hash": "..."
        }
    """
    tx_hash, error = extract_transaction_hash()

    if error is not None:
        return error

    logger.info(
        "API: Analyzing Bitcoin transaction: %s",
        tx_hash,
    )

    report = btc_controller.transaction_analyzer(
        tx_hash
    )

    return jsonify(report)


# ============================================================================
# TRON Wallet Endpoint
# ============================================================================

@app.route(
    "/api/tron/wallet/inspect",
    methods=["POST"],
)
@api_route("TRON wallet inspection")
def inspect_tron_wallet():
    """
    Inspect a TRON wallet address.

    Request body:
        {
            "address": "T..."
        }
    """
    address, error = extract_address()

    if error is not None:
        return error

    logger.info(
        "API: Inspecting TRON wallet: %s",
        address,
    )

    report = tron_controller.wallet_inspector(
        address
    )

    return jsonify(report)


# ============================================================================
# TRON Contract Endpoint
# ============================================================================

@app.route(
    "/api/tron/contract/inspect",
    methods=["POST"],
)
@api_route("TRON contract inspection")
def inspect_tron_contract():
    """
    Inspect a TRON smart contract.

    Request body:
        {
            "address": "T..."
        }
    """
    address, error = extract_address()

    if error is not None:
        return error

    logger.info(
        "API: Inspecting TRON contract: %s",
        address,
    )

    report = tron_controller.contract_inspector(
        address
    )

    return jsonify(report)


# ============================================================================
# TRON Token Endpoint
# ============================================================================

@app.route(
    "/api/tron/token/inspect",
    methods=["POST"],
)
@api_route("TRON token inspection")
def inspect_tron_token():
    """
    Inspect a TRC-20 token.

    Request body:
        {
            "address": "T..."
        }
    """
    address, error = extract_address()

    if error is not None:
        return error

    logger.info(
        "API: Inspecting TRON token: %s",
        address,
    )

    report = tron_controller.token_inspector(
        address
    )

    return jsonify(report)
# ============================================================================
# Node Validation Endpoint
# ============================================================================

@app.route(
    "/api/node/validate",
    methods=["POST"],
)
@api_route("Node validation")
def validate_node():
    """
    Validate a blockchain node.

    Request body:
        {
            "address": "https://..."
        }

    The existing API contract uses the ``address`` field for the
    node/RPC endpoint.
    """
    data, error = get_json_body()

    if error is not None:
        return error

    rpc_url = data.get("address")

    logger.info(
        "API: Validating node: %s",
        rpc_url or "default",
    )

    report = eth_controller.node_validator(
        rpc_url
    )

    return jsonify(report)


# ============================================================================
# Application Startup
# ============================================================================

def create_app() -> Flask:
    """
    Return the configured Flask application.

    The application object is already initialized at module level.
    This factory is provided for WSGI servers and testing without
    changing the existing ``app`` entry point.
    """
    return app


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    logger.info(
        "Starting Flask API server on %s:%s",
        DEFAULT_HOST,
        DEFAULT_PORT,
    )

    logger.info(
        "API Documentation available at "
        "http://localhost:%s/api/docs",
        DEFAULT_PORT,
    )

    app.run(
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        debug=True,
    )