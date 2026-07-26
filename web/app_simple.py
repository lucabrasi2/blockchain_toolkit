"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
web.app_simple

Purpose
-------
Flask web interface for UBP (without WebSocket).

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

import sqlite3
from flask import Flask, render_template, request, jsonify, session, flash, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from datetime import datetime
from functools import wraps

from controllers.ethereum_controller import EthereumController
from controllers.bitcoin_controller import BitcoinController
from controllers.tron_controller import TronController
from core.logger import get_logger

# Import authentication
from web.auth import auth_bp, load_user, get_user_manager, require_api_key, authenticate_api_key

# Import permissions
from web.permissions import require_permission, Permission, require_role, has_permission

# Import WebSocket
from web.ws import socketio, init_socketio, start_monitoring

logger = get_logger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# Setup authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.user_loader(load_user)

# Setup bcrypt
bcrypt = Bcrypt(app)

# Register auth blueprint
app.register_blueprint(auth_bp)

# Make current_user available in templates
app.jinja_env.globals['current_user'] = current_user

# Enable CORS
CORS(app)

# Initialize controllers
logger.info("Initializing controllers...")
eth_controller = EthereumController()
btc_controller = BitcoinController()
tron_controller = TronController()
logger.info("Controllers initialized.")


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


def require_api_key(func):
    """Decorator to require API key authentication."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = authenticate_api_key(request)
        if user:
            request.user = user
            return func(*args, **kwargs)
        return jsonify({"error": "Invalid or missing API key"}), 401
    return wrapper


# ============ Page Routes ============

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


@app.route('/dashboard')
@login_required
@require_permission(Permission.VIEW_DASHBOARD)
def dashboard_page():
    """Dashboard page."""
    return render_template('dashboard.html')


@app.route('/history')
@login_required
@require_permission(Permission.VIEW_HISTORY)
def history_page():
    """History page."""
    return render_template('history.html')


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
        
        # Save to database
        try:
            from database import get_db_manager
            db = get_db_manager()
            db.save_wallet_inspection(address, 'ethereum', report)
        except Exception as e:
            logger.warning(f"Could not save to database: {e}")
        
        return jsonify(convert_to_serializable(report))
    except Exception as e:
        logger.error(f"Ethereum wallet error: {e}")
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


# ============ Dashboard & History API Endpoints ============

@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
def dashboard_stats():
    """Get dashboard statistics."""
    try:
        from database import get_db_manager
        db = get_db_manager()
        
        with db.get_session() as session:
            from database.models import WalletInspection, ContractInspection, TransactionHistory, CacheEntry
            
            eth_wallets = session.query(WalletInspection).filter(WalletInspection.blockchain == 'ethereum').count()
            btc_wallets = session.query(WalletInspection).filter(WalletInspection.blockchain == 'bitcoin').count()
            tron_wallets = session.query(WalletInspection).filter(WalletInspection.blockchain == 'tron').count()
            
            eth_contracts = session.query(ContractInspection).filter(ContractInspection.blockchain == 'ethereum').count()
            tron_contracts = session.query(ContractInspection).filter(ContractInspection.blockchain == 'tron').count()
            
            total_transactions = session.query(TransactionHistory).count()
            cache_entries = session.query(CacheEntry).count()
            
            return jsonify({
                "total_inspections": eth_wallets + btc_wallets + tron_wallets + eth_contracts + tron_contracts,
                "ethereum": eth_wallets + eth_contracts,
                "bitcoin": btc_wallets,
                "tron": tron_wallets + tron_contracts,
                "total_transactions": total_transactions,
                "cache_entries": cache_entries,
            })
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/dashboard/recent', methods=['GET'])
@login_required
def dashboard_recent():
    """Get recent activity."""
    try:
        from database import get_db_manager
        db = get_db_manager()
        
        with db.get_session() as session:
            from database.models import WalletInspection, ContractInspection, TransactionHistory
            
            results = []
            
            wallets = session.query(WalletInspection).order_by(WalletInspection.created_at.desc()).limit(10).all()
            for w in wallets:
                results.append({
                    "type": "wallet",
                    "blockchain": w.blockchain,
                    "address": w.address,
                    "created_at": w.created_at.strftime("%Y-%m-%d %H:%M") if w.created_at else None,
                })
            
            contracts = session.query(ContractInspection).order_by(ContractInspection.created_at.desc()).limit(10).all()
            for c in contracts:
                results.append({
                    "type": "contract",
                    "blockchain": c.blockchain,
                    "address": c.address,
                    "created_at": c.created_at.strftime("%Y-%m-%d %H:%M") if c.created_at else None,
                })
            
            txs = session.query(TransactionHistory).order_by(TransactionHistory.created_at.desc()).limit(10).all()
            for t in txs:
                results.append({
                    "type": "transaction",
                    "blockchain": t.blockchain,
                    "tx_hash": t.tx_hash,
                    "status": t.status,
                    "created_at": t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else None,
                })
            
            results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return jsonify(results[:20])
    except Exception as e:
        logger.error(f"Dashboard recent error: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/history', methods=['GET'])
@login_required
def history():
    """Get history with filters."""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        blockchain = request.args.get('blockchain', '')
        type_filter = request.args.get('type', '')
        search = request.args.get('search', '')
        
        from database import get_db_manager
        db = get_db_manager()
        
        offset = (page - 1) * limit
        
        with db.get_session() as session:
            from database.models import WalletInspection, ContractInspection, TransactionHistory
            
            items = []
            
            query = session.query(WalletInspection)
            if blockchain:
                query = query.filter(WalletInspection.blockchain == blockchain)
            if search:
                query = query.filter(WalletInspection.address.contains(search))
            wallets = query.order_by(WalletInspection.created_at.desc()).limit(limit).offset(offset).all()
            for w in wallets:
                items.append({
                    "type": "wallet",
                    "blockchain": w.blockchain,
                    "address": w.address,
                    "details": f"Balance: {w.balance_eth or w.balance_btc or w.balance_trx or '0'}",
                    "status": True,
                    "created_at": w.created_at.strftime("%Y-%m-%d %H:%M") if w.created_at else None,
                })
            
            if not type_filter or type_filter == 'contract':
                query = session.query(ContractInspection)
                if blockchain:
                    query = query.filter(ContractInspection.blockchain == blockchain)
                if search:
                    query = query.filter(ContractInspection.address.contains(search))
                contracts = query.order_by(ContractInspection.created_at.desc()).limit(limit).offset(offset).all()
                for c in contracts:
                    items.append({
                        "type": "contract",
                        "blockchain": c.blockchain,
                        "address": c.address,
                        "details": f"{c.name or 'Unknown'} ({c.symbol or 'N/A'})",
                        "status": True,
                        "created_at": c.created_at.strftime("%Y-%m-%d %H:%M") if c.created_at else None,
                    })
            
            if not type_filter or type_filter == 'transaction':
                query = session.query(TransactionHistory)
                if blockchain:
                    query = query.filter(TransactionHistory.blockchain == blockchain)
                if search:
                    query = query.filter(TransactionHistory.tx_hash.contains(search))
                txs = query.order_by(TransactionHistory.created_at.desc()).limit(limit).offset(offset).all()
                for t in txs:
                    items.append({
                        "type": "transaction",
                        "blockchain": t.blockchain,
                        "tx_hash": t.tx_hash,
                        "details": f"From: {t.from_address[:10] if t.from_address else 'N/A'}...",
                        "status": t.status,
                        "created_at": t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else None,
                    })
            
            items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            total = len(items)
            
            return jsonify({
                "items": items[:limit],
                "total": total,
                "page": page,
                "total_pages": (total + limit - 1) // limit if total > 0 else 1,
            })
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({"error": str(e)}), 400


# ============ Export Endpoints ============

@app.route('/api/export/<export_type>', methods=['GET'])
@login_required
@require_permission(Permission.EXPORT_DATA)
def export_data(export_type):
    """Export data to CSV."""
    try:
        from database import get_db_manager
        db = get_db_manager()
        
        with db.get_session() as session:
            from database.models import WalletInspection, ContractInspection, TransactionHistory
            
            results = []
            
            if export_type in ['wallet', 'all']:
                wallets = session.query(WalletInspection).order_by(WalletInspection.created_at.desc()).all()
                for w in wallets:
                    results.append({
                        "type": "wallet",
                        "blockchain": w.blockchain,
                        "address": w.address,
                        "balance": float(w.balance_eth) if w.balance_eth else float(w.balance_btc) if w.balance_btc else float(w.balance_trx) if w.balance_trx else 0,
                        "classification": w.classification,
                        "created_at": w.created_at.strftime("%Y-%m-%d %H:%M") if w.created_at else None,
                    })
            
            if export_type in ['contract', 'all']:
                contracts = session.query(ContractInspection).order_by(ContractInspection.created_at.desc()).all()
                for c in contracts:
                    results.append({
                        "type": "contract",
                        "blockchain": c.blockchain,
                        "address": c.address,
                        "name": c.name,
                        "symbol": c.symbol,
                        "standard": c.standard,
                        "created_at": c.created_at.strftime("%Y-%m-%d %H:%M") if c.created_at else None,
                    })
            
            if export_type in ['transaction', 'all']:
                txs = session.query(TransactionHistory).order_by(TransactionHistory.created_at.desc()).all()
                for t in txs:
                    results.append({
                        "type": "transaction",
                        "blockchain": t.blockchain,
                        "tx_hash": t.tx_hash,
                        "from": t.from_address,
                        "to": t.to_address,
                        "value": float(t.value_eth) if t.value_eth else float(t.value_btc) if t.value_btc else float(t.value_trx) if t.value_trx else 0,
                        "status": "Success" if t.status else "Failed" if t.status is False else "Pending",
                        "created_at": t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else None,
                    })
            
            return jsonify(results)
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({"error": str(e)}), 400


# ============ User Management Endpoints (Admin Only) ============

@app.route('/api/admin/users', methods=['GET'])
@login_required
@require_role('admin')
def admin_users():
    """Get all users (admin only)."""
    try:
        from database import get_db_manager
        db = get_db_manager()
        
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, role, created_at, last_login, is_active FROM users')
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            users.append({
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "role": row[3],
                "created_at": row[4],
                "last_login": row[5],
                "is_active": bool(row[6]),
            })
        
        return jsonify(users)
    except Exception as e:
        logger.error(f"Admin users error: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/admin/users/<user_id>/role', methods=['PUT'])
@login_required
@require_role('admin')
def admin_update_role(user_id):
    """Update user role (admin only)."""
    try:
        data = request.json
        role = data.get('role')
        
        if role not in ['admin', 'user', 'viewer', 'api']:
            return jsonify({"error": "Invalid role"}), 400
        
        from database import get_db_manager
        db = get_db_manager()
        
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET role = ? WHERE id = ?', (role, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": f"User role updated to {role}"})
    except Exception as e:
        logger.error(f"Admin update role error: {e}")
        return jsonify({"error": str(e)}), 400


# ============ Main Entry Point ============

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🌐 Universal Blockchain Platform - Web Interface")
    logger.info("=" * 60)
    logger.info(f"📍 URL: http://0.0.0.0:5000")
    logger.info(f"📍 Dashboard: http://localhost:5000/dashboard")
    logger.info(f"📍 History: http://localhost:5000/history")
    logger.info(f"📍 Login: http://localhost:5000/auth/login")
    logger.info(f"📍 Register: http://localhost:5000/auth/register")
    logger.info(f"📍 Profile: http://localhost:5000/auth/profile")
    logger.info("=" * 60)
    logger.info("🔌 WebSocket running for real-time updates")
    logger.info("=" * 60)
    
    # Initialize SocketIO
    init_socketio(app)
    
    # Start monitoring threads
    start_monitoring()
    
    # Run with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)


###############################################################################
# End of File
###############################################################################