"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
api.mobile

Purpose
-------
Mobile API Blueprint for the UBP React Native / Expo client.

Architecture
------------
This module is an HTTP adapter only.

Business logic remains in:
    - services.user_service
    - services.wallet_service
    - blockchain controllers
    - database models

Mobile authentication uses a signed, time-limited access token.
The user's permanent API key is not exposed to the mobile client.
===============================================================================
"""

from __future__ import annotations

from datetime import timedelta
from functools import wraps

from flask import Blueprint, current_app, jsonify, request
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import URLSafeTimedSerializer


# =============================================================================
# Blueprint
# =============================================================================

mobile_bp = Blueprint(
    "mobile",
    __name__,
    url_prefix="/api/mobile",
)


# =============================================================================
# Token Configuration
# =============================================================================

MOBILE_TOKEN_MAX_AGE = 60 * 60 * 24


def _token_serializer() -> URLSafeTimedSerializer:
    """
    Create the serializer used for mobile access tokens.

    The Flask application's SECRET_KEY is used as the signing secret.
    """
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"],
        salt="ubp-mobile-access-token",
    )


def _create_access_token(user) -> str:
    """
    Create a signed mobile access token for a user.
    """
    serializer = _token_serializer()

    return serializer.dumps(
        {
            "user_id": str(user.id),
            "username": user.username,
        }
    )


def _decode_access_token(token: str):
    """
    Validate and decode a mobile access token.

    Returns:
        Token payload on success.
        None on invalid or expired token.
    """
    serializer = _token_serializer()

    try:
        return serializer.loads(
            token,
            max_age=MOBILE_TOKEN_MAX_AGE,
        )
    except (BadSignature, SignatureExpired):
        return None


def _get_bearer_token():
    """
    Extract a Bearer token from the Authorization header.
    """
    authorization = request.headers.get("Authorization", "")

    if not authorization:
        return None

    parts = authorization.split(" ", 1)

    if len(parts) != 2:
        return None

    scheme, token = parts

    if scheme.lower() != "bearer":
        return None

    return token.strip() or None


def mobile_auth_required(func):
    """
    Require a valid mobile Bearer token.

    The authenticated user is attached to request.mobile_user.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = _get_bearer_token()

        if not token:
            return jsonify(
                {
                    "success": False,
                    "error": "Missing Bearer token",
                }
            ), 401

        payload = _decode_access_token(token)

        if not payload:
            return jsonify(
                {
                    "success": False,
                    "error": "Invalid or expired access token",
                }
            ), 401

        try:
            from services.user_service import UserService

            user_service = UserService()
            user = user_service.get_user_by_id(payload["user_id"])

            if not user:
                return jsonify(
                    {
                        "success": False,
                        "error": "User not found",
                    }
                ), 401

            if not user.is_active:
                return jsonify(
                    {
                        "success": False,
                        "error": "User account is inactive",
                    }
                ), 403

            request.mobile_user = user

        except Exception as exc:
            current_app.logger.error(
                "Mobile authentication error: %s",
                exc,
            )

            return jsonify(
                {
                    "success": False,
                    "error": "Authentication service unavailable",
                }
            ), 500

        return func(*args, **kwargs)

    return wrapper


# =============================================================================
# Health
# =============================================================================

@mobile_bp.get("/health")
def mobile_health():
    """
    Return the health status of the mobile API.
    """
    return jsonify(
        {
            "success": True,
            "service": "UBP Mobile API",
            "status": "healthy",
        }
    ), 200


# =============================================================================
# Authentication
# =============================================================================

@mobile_bp.post("/auth/register")
def mobile_register():
    """
    Register a new mobile user.

    Expected JSON:

        {
            "username": "...",
            "email": "...",
            "password": "..."
        }
    """
    data = request.get_json(silent=True) or {}

    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")

    if not username:
        return jsonify(
            {
                "success": False,
                "error": "Username is required",
            }
        ), 400

    if not email:
        return jsonify(
            {
                "success": False,
                "error": "Email is required",
            }
        ), 400

    if not password:
        return jsonify(
            {
                "success": False,
                "error": "Password is required",
            }
        ), 400

    if len(password) < 8:
        return jsonify(
            {
                "success": False,
                "error": "Password must contain at least 8 characters",
            }
        ), 400

    try:
        from services.user_service import UserService

        user_service = UserService()

        user = user_service.create_user(
            username=username,
            email=email,
            password=password,
        )

        if not user:
            return jsonify(
                {
                    "success": False,
                    "error": "Unable to create user",
                }
            ), 400

        token = _create_access_token(user)

        return jsonify(
            {
                "success": True,
                "message": "Registration successful",
                "token": token,
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                },
            }
        ), 201

    except Exception as exc:
        current_app.logger.error(
            "Mobile registration error: %s",
            exc,
        )

        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 400


@mobile_bp.post("/auth/login")
def mobile_login():
    """
    Authenticate a mobile user.

    Expected JSON:

        {
            "username": "...",
            "password": "..."
        }

    The username may also be an email address if supported by UserService.
    """
    data = request.get_json(silent=True) or {}

    username = str(data.get("username", "")).strip()
    password = data.get("password", "")

    if not username:
        return jsonify(
            {
                "success": False,
                "error": "Username is required",
            }
        ), 400

    if not password:
        return jsonify(
            {
                "success": False,
                "error": "Password is required",
            }
        ), 400

    try:
        from services.user_service import UserService

        user_service = UserService()

        user = user_service.authenticate(
            username=username,
            password=password,
        )

        if not user:
            return jsonify(
                {
                    "success": False,
                    "error": "Invalid username or password",
                }
            ), 401

        if not user.is_active:
            return jsonify(
                {
                    "success": False,
                    "error": "User account is inactive",
                }
            ), 403

        token = _create_access_token(user)

        return jsonify(
            {
                "success": True,
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                },
            }
        ), 200

    except Exception as exc:
        current_app.logger.error(
            "Mobile login error: %s",
            exc,
        )

        return jsonify(
            {
                "success": False,
                "error": "Authentication failed",
            }
        ), 401


@mobile_bp.get("/auth/me")
@mobile_auth_required
def mobile_me():
    """
    Return the currently authenticated mobile user.
    """
    user = request.mobile_user

    return jsonify(
        {
            "success": True,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "default_network": user.default_network,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
            },
        }
    ), 200


@mobile_bp.post("/auth/logout")
@mobile_auth_required
def mobile_logout():
    """
    Mobile logout endpoint.

    The current token is stateless, so logout is primarily a client-side
    operation: the mobile application must remove its stored token.

    A future server-side token revocation mechanism can be added if required.
    """
    return jsonify(
        {
            "success": True,
            "message": "Logout successful",
        }
    ), 200


# =============================================================================
# Dashboard
# =============================================================================

@mobile_bp.get("/dashboard/stats")
@mobile_auth_required
def mobile_dashboard_stats():
    """
    Return dashboard statistics for the authenticated user.

    Returns:
        {
            "success": True,
            "data": {
                "total_wallets": 0,
                "total_transactions": 0,
                "by_blockchain": {
                    "ethereum": {"wallets": 0, "transactions": 0},
                    "bitcoin": {"wallets": 0, "transactions": 0},
                    "tron": {"wallets": 0, "transactions": 0}
                },
                "recent_activity": [
                    {
                        "type": "wallet_created" | "transaction",
                        "blockchain": "ethereum",
                        "address": "...",
                        "amount": null,
                        "created_at": "..."
                    }
                ]
            }
        }
    """
    try:
        user = request.mobile_user

        from services.wallet_service import WalletService
        from database.database import get_db_manager
        from database.models import Wallet, UserTransaction, WalletInspection

        wallet_service = WalletService()

        # Get all user wallets from the database
        db = get_db_manager()
        with db.get_session() as session:
            # Count wallets by blockchain
            wallets = session.query(Wallet).filter(
                Wallet.user_id == user.id,
                Wallet.is_active == True
            ).all()

            total_wallets = len(wallets)

            # Initialize blockchain counts
            blockchain_stats = {
                "ethereum": {"wallets": 0, "transactions": 0},
                "bitcoin": {"wallets": 0, "transactions": 0},
                "tron": {"wallets": 0, "transactions": 0},
            }

            # Get wallet IDs for transaction count
            wallet_ids = [str(w.id) for w in wallets]

            for wallet in wallets:
                blockchain = wallet.blockchain.lower()
                if blockchain in blockchain_stats:
                    blockchain_stats[blockchain]["wallets"] += 1

            # Count user transactions by blockchain
            if wallet_ids:
                from uuid import UUID
                wallet_uuids = [UUID(wid) for wid in wallet_ids]

                transactions = session.query(UserTransaction).filter(
                    UserTransaction.wallet_id.in_(wallet_uuids)
                ).all()

                total_transactions = len(transactions)

                for tx in transactions:
                    blockchain = tx.blockchain.lower()
                    if blockchain in blockchain_stats:
                        blockchain_stats[blockchain]["transactions"] += 1
            else:
                total_transactions = 0

            # Get recent activity (last 10 events)
            recent_activity = []

            # Get recent wallet inspections
            wallet_addresses = [w.address for w in wallets]
            if wallet_addresses:
                inspections = session.query(WalletInspection).filter(
                    WalletInspection.address.in_(wallet_addresses)
                ).order_by(
                    WalletInspection.created_at.desc()
                ).limit(5).all()

                for insp in inspections:
                    recent_activity.append({
                        "type": "wallet_inspection",
                        "blockchain": insp.blockchain,
                        "address": insp.address,
                        "amount": None,
                        "created_at": insp.created_at.isoformat() if insp.created_at else None,
                    })

            # Get recent transactions
            if wallet_ids:
                wallet_uuids = [UUID(wid) for wid in wallet_ids]
                recent_txs = session.query(UserTransaction).filter(
                    UserTransaction.wallet_id.in_(wallet_uuids)
                ).order_by(
                    UserTransaction.created_at.desc()
                ).limit(5).all()

                for tx in recent_txs:
                    recent_activity.append({
                        "type": "transaction",
                        "blockchain": tx.blockchain,
                        "address": tx.to_address,
                        "amount": float(tx.amount) if tx.amount else None,
                        "asset": tx.asset,
                        "status": tx.status,
                        "created_at": tx.created_at.isoformat() if tx.created_at else None,
                    })

            # Sort by created_at (most recent first) and limit to 10
            recent_activity.sort(
                key=lambda x: x.get("created_at", ""),
                reverse=True
            )
            recent_activity = recent_activity[:10]

        return jsonify(
            {
                "success": True,
                "data": {
                    "total_wallets": total_wallets,
                    "total_transactions": total_transactions,
                    "by_blockchain": blockchain_stats,
                    "recent_activity": recent_activity,
                },
            }
        ), 200

    except Exception as exc:
        current_app.logger.error(
            "Mobile dashboard error: %s",
            exc,
        )
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 500


# =============================================================================
# Wallet Management
# =============================================================================

@mobile_bp.post("/wallets/create")
@mobile_auth_required
def mobile_create_wallet():
    """
    Create a new wallet for the authenticated user.

    Expected JSON:
        {
            "blockchain": "ethereum" | "bitcoin" | "tron",
            "label": "My ETH Wallet"
        }

    Returns:
        {
            "success": True,
            "wallet": {
                "id": "uuid",
                "wallet_id": "eth_123abc",
                "address": "0x...",
                "blockchain": "ethereum",
                "network": "mainnet",
                "label": "My ETH Wallet",
                "created_at": "2026-01-01T00:00:00"
            }
        }
    """
    try:
        user = request.mobile_user
        data = request.get_json(silent=True) or {}

        blockchain = str(data.get("blockchain", "")).strip().lower()
        label = str(data.get("label", "")).strip()

        if not blockchain:
            return jsonify(
                {
                    "success": False,
                    "error": "Blockchain is required",
                }
            ), 400

        if blockchain not in ["ethereum", "bitcoin", "tron"]:
            return jsonify(
                {
                    "success": False,
                    "error": "Blockchain must be ethereum, bitcoin, or tron",
                }
            ), 400

        if not label:
            label = f"{blockchain.capitalize()} Wallet"

        from services.wallet_service import WalletService

        wallet_service = WalletService()
        wallet = wallet_service.create_wallet(
            user_id=user.id,
            blockchain=blockchain,
            label=label,
        )

        if not wallet:
            return jsonify(
                {
                    "success": False,
                    "error": "Failed to create wallet",
                }
            ), 500

        return jsonify(
            {
                "success": True,
                "wallet": {
                    "id": str(wallet.get("id")),
                    "wallet_id": wallet.get("wallet_id"),
                    "address": wallet.get("address"),
                    "blockchain": wallet.get("blockchain"),
                    "network": wallet.get("network", "mainnet"),
                    "label": wallet.get("label"),
                    "created_at": wallet.get("created_at"),
                },
            }
        ), 201

    except Exception as exc:
        current_app.logger.error(
            "Mobile wallet creation error: %s",
            exc,
        )
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 500


@mobile_bp.get("/wallets")
@mobile_auth_required
def mobile_list_wallets():
    """
    List all wallets for the authenticated user.

    Returns:
        {
            "success": True,
            "wallets": [
                {
                    "id": "uuid",
                    "wallet_id": "eth_123abc",
                    "address": "0x...",
                    "blockchain": "ethereum",
                    "network": "mainnet",
                    "label": "My ETH Wallet",
                    "created_at": "2026-01-01T00:00:00"
                }
            ]
        }
    """
    try:
        user = request.mobile_user

        from services.wallet_service import WalletService

        wallet_service = WalletService()
        wallets = wallet_service.get_user_wallets(user.id)

        return jsonify(
            {
                "success": True,
                "wallets": wallets,
            }
        ), 200

    except Exception as exc:
        current_app.logger.error(
            "Mobile list wallets error: %s",
            exc,
        )
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 500


@mobile_bp.get("/wallets/<wallet_id>/balance")
@mobile_auth_required
def mobile_get_wallet_balance(wallet_id: str):
    """
    Get the balance for a specific wallet.

    Returns:
        {
            "success": True,
            "balance": {
                "balance": 1.5,
                "symbol": "ETH",
                "address": "0x...",
                "decimals": 18
            }
        }
    """
    try:
        user = request.mobile_user

        from services.wallet_service import WalletService

        wallet_service = WalletService()

        # Verify wallet belongs to user
        wallets = wallet_service.get_user_wallets(user.id)
        wallet = next((w for w in wallets if w.get("wallet_id") == wallet_id), None)

        if not wallet:
            return jsonify(
                {
                    "success": False,
                    "error": "Wallet not found or access denied",
                }
            ), 404

        balance = wallet_service.get_wallet_balance(wallet_id)

        if "error" in balance:
            return jsonify(
                {
                    "success": False,
                    "error": balance["error"],
                }
            ), 400

        return jsonify(
            {
                "success": True,
                "balance": balance,
            }
        ), 200

    except Exception as exc:
        current_app.logger.error(
            "Mobile get balance error: %s",
            exc,
        )
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 500


# =============================================================================
# Transaction Management
# =============================================================================

@mobile_bp.post("/wallets/<wallet_id>/send")
@mobile_auth_required
def mobile_send_transaction(wallet_id: str):
    """
    Send a transaction from a user's wallet.

    Expected JSON:
        {
            "to_address": "0x...",
            "amount": 0.001
        }

    Returns:
        {
            "success": True,
            "transaction": {
                "tx_hash": "0x...",
                "from": "0x...",
                "to": "0x...",
                "amount": 0.001,
                "asset": "ETH",
                "fee": 0.0001,
                "status": "pending"
            }
        }
    """
    try:
        user = request.mobile_user
        data = request.get_json(silent=True) or {}

        to_address = str(data.get("to_address", "")).strip()
        amount = data.get("amount")

        if not to_address:
            return jsonify(
                {
                    "success": False,
                    "error": "Recipient address is required",
                }
            ), 400

        if amount is None:
            return jsonify(
                {
                    "success": False,
                    "error": "Amount is required",
                }
            ), 400

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return jsonify(
                {
                    "success": False,
                    "error": "Amount must be a valid number",
                }
            ), 400

        if amount <= 0:
            return jsonify(
                {
                    "success": False,
                    "error": "Amount must be greater than 0",
                }
            ), 400

        from services.wallet_service import WalletService

        wallet_service = WalletService()

        # Verify wallet belongs to user
        wallets = wallet_service.get_user_wallets(user.id)
        wallet = next((w for w in wallets if w.get("wallet_id") == wallet_id), None)

        if not wallet:
            return jsonify(
                {
                    "success": False,
                    "error": "Wallet not found or access denied",
                }
            ), 404

        # Send the transaction
        result = wallet_service.send_transaction(
            wallet_id=wallet_id,
            to_address=to_address,
            amount=amount
        )

        if "error" in result:
            return jsonify(
                {
                    "success": False,
                    "error": result["error"],
                }
            ), 400

        return jsonify(
            {
                "success": True,
                "transaction": {
                    "tx_hash": result.get("tx_hash"),
                    "from": result.get("from"),
                    "to": result.get("to"),
                    "amount": result.get("amount"),
                    "asset": result.get("asset", "ETH"),
                    "fee": result.get("fee"),
                    "status": result.get("status", "pending"),
                },
            }
        ), 200

    except Exception as exc:
        current_app.logger.error(
            "Mobile send transaction error: %s",
            exc,
        )
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 500


# =============================================================================
# End of Module
# =============================================================================