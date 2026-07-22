"""
Universal Blockchain Platform (UBP)

Module:
    Flask API

Purpose:
    REST API for the Universal Blockchain Platform using Flask.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

import sys
import os
import json
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask_cors import CORS

from controllers.ethereum_controller import EthereumController
from controllers.bitcoin_controller import BitcoinController
from controllers.tron_controller import TronController
from ethereum.gas import get_gas_optimizer
from core.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize controllers
logger.info("Initializing controllers for Flask API...")
eth_controller = EthereumController()
btc_controller = BitcoinController()
tron_controller = TronController()
logger.info("Flask API initialized successfully.")


# ============ Root & Health Endpoints ============

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information."""
    return jsonify({
        "name": "Universal Blockchain Platform API",
        "version": "2.0.0",
        "status": "operational",
        "blockchains": ["Ethereum", "Bitcoin", "TRON"],
        "endpoints": {
            "ethereum": {
                "wallet": "/api/ethereum/wallet/inspect",
                "contract": "/api/ethereum/contract/inspect",
                "token": "/api/ethereum/token/inspect",
                "block": "/api/ethereum/block/explore",
                "transaction": "/api/ethereum/transaction/analyze",
                "gas": "/api/ethereum/gas/price"
            },
            "bitcoin": {
                "wallet": "/api/bitcoin/wallet/inspect",
                "block": "/api/bitcoin/block/explore",
                "transaction": "/api/bitcoin/transaction/analyze"
            },
            "tron": {
                "wallet": "/api/tron/wallet/inspect",
                "contract": "/api/tron/contract/inspect",
                "token": "/api/tron/token/inspect"
            }
        },
        "documentation": "/api/docs",
        "health": "/health"
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        w3 = eth_controller.connection
        connected = w3.is_connected()
        chain_id = w3.eth.chain_id if connected else None
        block_number = w3.eth.block_number if connected else None
    except Exception as e:
        logger.error(f"Health check error: {e}")
        connected = False
        chain_id = None
        block_number = None

    return jsonify({
        "status": "healthy" if connected else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "blockchain": "Ethereum",
        "chain_id": chain_id,
        "block_number": block_number,
        "connected": connected
    })


@app.route('/api/docs', methods=['GET'])
def api_docs():
    """Simple API documentation."""
    return jsonify({
        "title": "Universal Blockchain Platform API",
        "version": "2.0.0",
        "description": "Enterprise-grade blockchain intelligence API",
        "endpoints": {
            "GET /": "API information",
            "GET /health": "Health check",
            "GET /api/docs": "This documentation",
            "GET /api/ethereum/gas/price": "Get current Ethereum gas price",
            "POST /api/ethereum/wallet/inspect": "Inspect Ethereum wallet",
            "POST /api/ethereum/contract/inspect": "Inspect Ethereum contract",
            "POST /api/ethereum/token/inspect": "Inspect ERC-20 token",
            "POST /api/ethereum/block/explore": "Explore Ethereum block",
            "POST /api/ethereum/transaction/analyze": "Analyze Ethereum transaction",
            "POST /api/bitcoin/wallet/inspect": "Inspect Bitcoin wallet",
            "POST /api/bitcoin/block/explore": "Explore Bitcoin block",
            "POST /api/bitcoin/transaction/analyze": "Analyze Bitcoin transaction",
            "POST /api/tron/wallet/inspect": "Inspect TRON wallet",
            "POST /api/tron/contract/inspect": "Inspect TRON contract",
            "POST /api/tron/token/inspect": "Inspect TRC-20 token"
        }
    })


# ============ Error Handlers ============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "message": "Please check the API documentation at /api/docs"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


# ============ Ethereum Endpoints ============

@app.route('/api/ethereum/wallet/inspect', methods=['POST'])
def inspect_ethereum_wallet():
    """
    Inspect an Ethereum wallet address.

    Request body:
    {
        "address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Request body required"}), 400

        address = data.get('address')
        if not address:
            return jsonify({"error": "Address required"}), 400

        logger.info(f"API: Inspecting Ethereum wallet: {address}")
        report = eth_controller.wallet_inspector(address)
        return jsonify(report)

    except Exception as e:
        logger.error(f"API Error - Wallet inspection: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/ethereum/contract/inspect', methods=['POST'])
def inspect_ethereum_contract():
    """
    Inspect an Ethereum contract address.

    Request body:
    {
        "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Request body required"}), 400

        address = data.get('address')
        if not address:
            return jsonify({"error": "Address required"}), 400

        logger.info(f"API: Inspecting Ethereum contract: {address}")
        report = eth_controller.contract_inspector(address)
        return jsonify(report)

    except Exception as e:
        logger.error(f"API Error - Contract inspection: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/ethereum/token/inspect', methods=['POST'])
def inspect_ethereum_token():
    """
    Inspect an ERC-20 token.

    Request body:
    {
        "address": "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Request body required"}), 400

        address = data.get('address')
        if not address:
            return jsonify({"error": "Address required"}), 400

        logger.info(f"API: Inspecting Ethereum token: {address}")
        report = eth_controller.token_inspector(address)
        return jsonify(report)

    except Exception as e:
        logger.error(f"API Error - Token inspection: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/ethereum/block/explore', methods=['POST'])
def explore_ethereum_block():
    """
    Explore an Ethereum block.

    Request body:
    {
        "block_identifier": "latest"
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Request body required"}), 400

        block_identifier = data.get('block_identifier')
        if not block_identifier:
            return jsonify({"error": "Block identifier required"}), 400

        logger.info(f"API: Exploring Ethereum block: {block_identifier}")
        report = eth_controller.block_explorer(block_identifier)
        return jsonify(report)

    except Exception as e:
        logger.error(f"API Error - Block exploration: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/ethereum/transaction/analyze', methods=['POST'])
def analyze_ethereum_transaction():
    """
    Analyze an Ethereum transaction.

    Request body:
    {
        "tx_hash": "0x4a7c5e8d9a5b0f5a5c8d9e5f4c7e5c8d9a5b0f5a"
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Request body required"}), 400

        tx_hash = data.get('tx_hash')
        if not tx_hash:
            return jsonify({"error": "Transaction hash required"}), 400

        logger.info(f"API: Analyzing Ethereum transaction: {tx_hash}")
        report = eth_controller.transaction_analyzer(tx_hash)
        return jsonify(report)

    except Exception as e:
        logger.error(f"API Error - Transaction analysis: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/ethereum/gas/price', methods=['GET'])
def get_ethereum_gas_price():
    """Get current Ethereum gas price."""
    try:
        logger.info("API: Getting Ethereum gas price")
        optimizer = get_gas_optimizer()
        gas_info = optimizer.get_gas_price()
        return jsonify(gas_info)

    except Exception as e:
        logger.error(f"API Error - Gas price: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/ethereum/gas/estimate', methods=['POST'])
def estimate_ethereum_gas():
    """
    Estimate Ethereum gas cost.

    Request body:
    {
        "gas_limit": 21000,
        "gas_price_gwei": 20
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Request body required"}), 400

        gas_limit = data.get('gas_limit', 21000)
        gas_price_gwei = data.get('gas_price_gwei')

        logger.info(f"API: Estimating gas cost - Limit: {gas_limit}")
        optimizer = get_gas_optimizer()
        estimate = optimizer.estimate_gas_cost(gas_limit, gas_price_gwei)
        return jsonify(estimate)

    except Exception as e:
        logger.error(f"API Error - Gas estimate: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/ethereum/gas/optimal', methods=['GET'])
def get_optimal_gas_price():
    """
    Get optimal gas price recommendations.

    Query params:
    urgency: slow | standard | fast | instant
    """
    try:
        urgency = request.args.get('urgency', 'standard')
        logger.info(f"API: Getting optimal gas price - Urgency: {urgency}")
        optimizer = get_gas_optimizer()
        recommendations = optimizer.get_optimal_gas_price(urgency)
        return jsonify(recommendations)

    except Exception as e:
        logger.error(f"API Error - Optimal gas: {e}")
        return jsonify({"error": str(e)}), 400


# ============ Bitcoin Endpoints ============

@app.route('/api/bitcoin/wallet/inspect', methods=['POST'])
def inspect_bitcoin_wallet():
    """
    Inspect a Bitcoin wallet address.

    Request body:
    {
        "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Request body required"}), 400

        address = data.get('address')
        if not address:
            return jsonify({"error": "Address required"}), 400

        logger.info(f"API: Inspecting Bitcoin wallet: {address}")
        report = btc_controller.wallet_inspector(address)
        return jsonify(report)

    except Exception as e:
        logger.error(f"API Error - Bitcoin wallet inspection: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/bitcoin/block/explore', methods=['POST'])
def explore_bitcoin_block():
    """
    Explore a Bitcoin block.

    Request body:
    {
        "block_identifier": "latest"
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Request body required"}), 400

        block_identifier = data.get('block_identifier')
        if not block_identifier:
            return jsonify({"error": "Block identifier required"}), 400

        logger.info(f"API: Exploring Bitcoin block: {block_identifier}")
        report = btc_controller.block_explorer(block_identifier)
        return jsonify(report)

    except Exception as e:
        logger.error(f"API Error - Bitcoin block exploration: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/bitcoin/transaction/analyze', methods=['POST'])
def analyze_bitcoin_transaction():
    """
    Analyze a Bitcoin transaction.

    Request body:
    {
        "tx_hash": "0x4a7c5e8d9a5b0f5a5c8d9e5f4c7e5c8d9a5b0f5a"
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Request body required"}), 400

        tx_hash = data.get('tx_hash')
        if not tx_hash:
            return jsonify({"error": "Transaction hash required"}), 400

        logger.info(f"API: Analyzing Bitcoin transaction: {tx_hash}")
        report = btc_controller.transaction_analyzer(tx_hash)
        return jsonify(report)

    except Exception as e:
        logger.error(f"API Error - Bitcoin transaction analysis: {e}")
        return jsonify({"error": str(e)}), 400


# ============ TRON Endpoints ============

@app.route('/api/tron/wallet/inspect', methods=['POST'])
def inspect_tron_wallet():
    """
    Inspect a TRON wallet address.

    Request body:
    {
        "address": "TYMrhPDPkLkHT2BzT1z3vN9FqXCCbNvT6x"
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Request body required"}), 400

        address = data.get('address')
        if not address:
            return jsonify({"error": "Address required"}), 400

        logger.info(f"API: Inspecting TRON wallet: {address}")
        report = tron_controller.wallet_inspector(address)
        return jsonify(report)

    except Exception as e:
        logger.error(f"API Error - TRON wallet inspection: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/tron/contract/inspect', methods=['POST'])
def inspect_tron_contract():
    """
    Inspect a TRON contract address.

    Request body:
    {
        "address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Request body required"}), 400

        address = data.get('address')
        if not address:
            return jsonify({"error": "Address required"}), 400

        logger.info(f"API: Inspecting TRON contract: {address}")
        report = tron_controller.contract_inspector(address)
        return jsonify(report)

    except Exception as e:
        logger.error(f"API Error - TRON contract inspection: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/tron/token/inspect', methods=['POST'])
def inspect_tron_token():
    """
    Inspect a TRC-20 token.

    Request body:
    {
        "address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Request body required"}), 400

        address = data.get('address')
        if not address:
            return jsonify({"error": "Address required"}), 400

        logger.info(f"API: Inspecting TRON token: {address}")
        report = tron_controller.token_inspector(address)
        return jsonify(report)

    except Exception as e:
        logger.error(f"API Error - TRON token inspection: {e}")
        return jsonify({"error": str(e)}), 400


# ============ Node Endpoints ============

@app.route('/api/node/validate', methods=['POST'])
def validate_node():
    """
    Validate a blockchain node.

    Request body:
    {
        "address": "https://mainnet.infura.io/v3/your-key"
    }
    """
    try:
        data = request.json
        rpc_url = data.get('address') if data else None

        logger.info(f"API: Validating node: {rpc_url or 'default'}")
        report = eth_controller.node_validator(rpc_url)
        return jsonify(report)

    except Exception as e:
        logger.error(f"API Error - Node validation: {e}")
        return jsonify({"error": str(e)}), 400


# ============ Main Entry Point ============

if __name__ == '__main__':
    logger.info("Starting Flask API server on http://0.0.0.0:8000")
    logger.info("API Documentation available at http://localhost:8000/api/docs")
    app.run(host='0.0.0.0', port=8000, debug=True)