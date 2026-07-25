"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
web.app

Purpose
-------
Flask web interface for UBP.

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

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from controllers.ethereum_controller import EthereumController
from controllers.bitcoin_controller import BitcoinController
from controllers.tron_controller import TronController
from core.logger import get_logger

logger = get_logger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize controllers
eth_controller = EthereumController()
btc_controller = BitcoinController()
tron_controller = TronController()


@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/ethereum')
def ethereum_page():
    """Ethereum page."""
    return render_template('ethereum.html')


@app.route('/bitcoin')
def bitcoin_page():
    """Bitcoin page."""
    return render_template('bitcoin.html')


@app.route('/tron')
def tron_page():
    """TRON page."""
    return render_template('tron.html')


# ============ Helper Functions ============

def convert_to_serializable(obj):
    """
    Convert bytes and HexBytes objects to strings for JSON serialization.
    """
    if isinstance(obj, bytes):
        return obj.hex()
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    else:
        return obj


# ============ Ethereum API Endpoints ============

@app.route('/api/ethereum/wallet', methods=['POST'])
def ethereum_wallet():
    """Inspect Ethereum wallet."""
    try:
        data = request.json
        address = data.get('address')
        if not address:
            return jsonify({"error": "Address required"}), 400
        report = eth_controller.wallet_inspector(address)
        return jsonify(convert_to_serializable(report))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/ethereum/contract', methods=['POST'])
def ethereum_contract():
    """Inspect Ethereum contract."""
    try:
        data = request.json
        address = data.get('address')
        if not address:
            return jsonify({"error": "Address required"}), 400
        report = eth_controller.contract_inspector(address)
        return jsonify(convert_to_serializable(report))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/ethereum/token', methods=['POST'])
def ethereum_token():
    """Inspect Ethereum token."""
    try:
        data = request.json
        address = data.get('address')
        if not address:
            return jsonify({"error": "Address required"}), 400
        report = eth_controller.token_inspector(address)
        return jsonify(convert_to_serializable(report))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/ethereum/block', methods=['POST'])
def ethereum_block():
    """Explore Ethereum block."""
    try:
        data = request.json
        block = data.get('block', 'latest')
        report = eth_controller.block_explorer(block)
        return jsonify(convert_to_serializable(report))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/ethereum/transaction', methods=['POST'])
def ethereum_transaction():
    """Analyze Ethereum transaction."""
    try:
        data = request.json
        tx_hash = data.get('tx_hash')
        if not tx_hash:
            return jsonify({"error": "Transaction hash required"}), 400
        report = eth_controller.transaction_analyzer(tx_hash)
        return jsonify(convert_to_serializable(report))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/ethereum/gas', methods=['GET'])
def ethereum_gas():
    """Get Ethereum gas price."""
    try:
        from ethereum.gas import get_gas_optimizer
        optimizer = get_gas_optimizer()
        return jsonify(convert_to_serializable(optimizer.get_gas_price()))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ============ Bitcoin API Endpoints ============

@app.route('/api/bitcoin/wallet', methods=['POST'])
def bitcoin_wallet():
    """Inspect Bitcoin wallet."""
    try:
        data = request.json
        address = data.get('address')
        if not address:
            return jsonify({"error": "Address required"}), 400
        report = btc_controller.wallet_inspector(address)
        return jsonify(convert_to_serializable(report))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/bitcoin/block', methods=['POST'])
def bitcoin_block():
    """Explore Bitcoin block."""
    try:
        data = request.json
        block = data.get('block', 'latest')
        report = btc_controller.block_explorer(block)
        return jsonify(convert_to_serializable(report))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/bitcoin/transaction', methods=['POST'])
def bitcoin_transaction():
    """Analyze Bitcoin transaction."""
    try:
        data = request.json
        tx_hash = data.get('tx_hash')
        if not tx_hash:
            return jsonify({"error": "Transaction hash required"}), 400
        report = btc_controller.transaction_analyzer(tx_hash)
        return jsonify(convert_to_serializable(report))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/bitcoin/fee', methods=['GET'])
def bitcoin_fee():
    """Get Bitcoin fee estimates."""
    try:
        from bitcoin.gas import get_fee_optimizer
        optimizer = get_fee_optimizer()
        return jsonify(convert_to_serializable(optimizer.get_fee_estimate()))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ============ TRON API Endpoints ============

@app.route('/api/tron/wallet', methods=['POST'])
def tron_wallet():
    """Inspect TRON wallet."""
    try:
        data = request.json
        address = data.get('address')
        if not address:
            return jsonify({"error": "Address required"}), 400
        report = tron_controller.wallet_inspector(address)
        return jsonify(convert_to_serializable(report))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/tron/contract', methods=['POST'])
def tron_contract():
    """Inspect TRON contract."""
    try:
        data = request.json
        address = data.get('address')
        if not address:
            return jsonify({"error": "Address required"}), 400
        report = tron_controller.contract_inspector(address)
        return jsonify(convert_to_serializable(report))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/tron/token', methods=['POST'])
def tron_token():
    """Inspect TRON token."""
    try:
        data = request.json
        address = data.get('address')
        if not address:
            return jsonify({"error": "Address required"}), 400
        report = tron_controller.token_inspector(address)
        return jsonify(convert_to_serializable(report))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/tron/block', methods=['POST'])
def tron_block():
    """Explore TRON block."""
    try:
        data = request.json
        block = data.get('block', 'latest')
        
        from tron.blocks import get_block, get_latest_block_number
        
        if block == 'latest':
            block_num = get_latest_block_number()
            report = get_block(block_num)
        else:
            report = get_block(int(block))
        
        return jsonify(convert_to_serializable(report))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/tron/transaction', methods=['POST'])
def tron_transaction():
    """Analyze TRON transaction."""
    try:
        data = request.json
        tx_hash = data.get('tx_hash')
        if not tx_hash:
            return jsonify({"error": "Transaction hash required"}), 400
        from tron.transactions import get_transaction
        report = get_transaction(tx_hash)
        return jsonify(convert_to_serializable(report))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    logger.info("Starting Web Interface on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)


###############################################################################
# End of File
###############################################################################
