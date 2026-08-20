"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
api.mobile

Purpose
-------
Mobile API HTTP adapter for the UBP React Native / Expo client.

Architecture
------------
This module is an HTTP adapter only.

Business logic remains in:
    - services.user_service
    - services.wallet_service
    - blockchain controllers
    - database models

Authentication
--------------
Mobile authentication uses a signed, time-limited access token.

The user's permanent API key is never exposed to the mobile client.
===============================================================================
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple

from flask import (
    Blueprint,
    current_app,
    jsonify,
    request,
)
from itsdangerous import (
    BadSignature,
    SignatureExpired,
    URLSafeTimedSerializer,
)


# =============================================================================
# Blueprint
# =============================================================================

mobile_bp = Blueprint(
    "mobile",
    __name__,
    url_prefix="/api/mobile",
)


# =============================================================================
# Configuration
# =============================================================================

MOBILE_TOKEN_MAX_AGE = 60 * 60 * 24

SUPPORTED_BLOCKCHAINS = frozenset(
    {
        "ethereum",
        "bitcoin",
        "tron",
    }
)

DEFAULT_PAGE_LIMIT = 20
MAX_PAGE_LIMIT = 100


# =============================================================================
# Response Helpers
# =============================================================================

def _success_response(
    data: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
    **extra: Any,
):
    """
    Return a consistent successful mobile API response.
    """
    payload: Dict[str, Any] = {
        "success": True,
    }

    if data:
        payload.update(data)

    if extra:
        payload.update(extra)

    return jsonify(payload), status_code


def _error_response(
    message: str,
    status_code: int = 400,
):
    """
    Return a consistent mobile API error response.
    """
    return jsonify(
        {
            "success": False,
            "error": message,
        }
    ), status_code


def _request_json() -> Dict[str, Any]:
    """
    Safely return the request JSON object.

    Invalid or missing JSON is represented as an empty dictionary.
    """
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {}

    return data


def _required_string(
    data: Dict[str, Any],
    field: str,
    message: Optional[str] = None,
    *,
    lowercase: bool = False,
) -> Tuple[Optional[str], Optional[Any]]:
    """
    Extract a required non-empty string field.

    Returns
    -------
    tuple
        ``(value, None)`` on success.
        ``(None, error_response)`` on failure.
    """
    value = data.get(field)

    if value is None:
        return None, _error_response(
            message or f"{field.replace('_', ' ').title()} is required",
            400,
        )

    value = str(value).strip()

    if not value:
        return None, _error_response(
            message or f"{field.replace('_', ' ').title()} is required",
            400,
        )

    if lowercase:
        value = value.lower()

    return value, None


# =============================================================================
# Service Helpers
# =============================================================================

def _get_user_service():
    """
    Lazily construct the user service.

    Lazy imports preserve the HTTP-adapter boundary and avoid unnecessary
    initialization when the mobile module is imported.
    """
    from services.user_service import UserService

    return UserService()


def _get_wallet_service():
    """
    Lazily construct the wallet service.
    """
    from services.wallet_service import WalletService

    return WalletService()


# =============================================================================
# User Serialization
# =============================================================================

def _serialize_user(
    user,
    *,
    include_network: bool = False,
) -> Dict[str, Any]:
    """
    Convert a UBP user model/service object into the mobile-safe
    representation.

    Sensitive fields such as passwords and permanent API keys are never
    included.
    """
    payload = {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
    }

    if include_network:
        payload["default_network"] = user.default_network

    return payload


# =============================================================================
# Wallet Ownership
# =============================================================================

def _get_owned_wallet(
    wallet_service,
    user_id,
    wallet_id,
):
    """
    Return a wallet owned by ``user_id``.

    Returning ``None`` ensures callers cannot operate on wallets belonging
    to another user.
    """
    wallets = wallet_service.get_user_wallets(user_id)

    return next(
        (
            wallet
            for wallet in wallets
            if wallet.get("wallet_id") == wallet_id
        ),
        None,
    )


def _require_owned_wallet(
    wallet_service,
    user_id,
    wallet_id,
):
    """
    Validate wallet ownership and return either the wallet or an HTTP error.
    """
    wallet = _get_owned_wallet(
        wallet_service,
        user_id,
        wallet_id,
    )

    if not wallet:
        return None, _error_response(
            "Wallet not found or access denied",
            404,
        )

    return wallet, None


# =============================================================================
# Pagination
# =============================================================================

def _parse_pagination():
    """
    Parse and validate transaction-history pagination parameters.
    """
    limit = request.args.get(
        "limit",
        DEFAULT_PAGE_LIMIT,
        type=int,
    )

    offset = request.args.get(
        "offset",
        0,
        type=int,
    )

    if limit is None or not 1 <= limit <= MAX_PAGE_LIMIT:
        return (
            None,
            None,
            "Limit must be between 1 and 100",
        )

    if offset is None or offset < 0:
        return (
            None,
            None,
            "Offset must be 0 or greater",
        )

    return limit, offset, None


# =============================================================================
# Mobile Access Tokens
# =============================================================================

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
    Create a signed mobile access token.
    """
    serializer = _token_serializer()

    return serializer.dumps(
        {
            "user_id": str(user.id),
            "username": user.username,
        }
    )


def _decode_access_token(
    token: str,
):
    """
    Validate and decode a mobile access token.

    Returns
    -------
    dict | None
        Token payload on success, otherwise ``None``.
    """
    if not token:
        return None

    serializer = _token_serializer()

    try:
        return serializer.loads(
            token,
            max_age=MOBILE_TOKEN_MAX_AGE,
        )

    except (
        BadSignature,
        SignatureExpired,
    ):
        return None


def _get_bearer_token() -> Optional[str]:
    """
    Extract a Bearer token from the Authorization header.
    """
    authorization = request.headers.get(
        "Authorization",
        "",
    ).strip()

    if not authorization:
        return None

    scheme, separator, token = authorization.partition(" ")

    if (
        not separator
        or scheme.lower() != "bearer"
    ):
        return None

    token = token.strip()

    return token or None


# =============================================================================
# Authentication Decorator
# =============================================================================

def mobile_auth_required(
    func: Callable,
) -> Callable:
    """
    Require a valid mobile Bearer token.

    The authenticated user is attached to:

        request.mobile_user
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        token = _get_bearer_token()

        if not token:
            return _error_response(
                "Missing Bearer token",
                401,
            )

        payload = _decode_access_token(token)

        if not payload:
            return _error_response(
                "Invalid or expired access token",
                401,
            )

        user_id = payload.get("user_id")

        if not user_id:
            return _error_response(
                "Invalid access token",
                401,
            )

        try:
            user_service = _get_user_service()

            user = user_service.get_user_by_id(
                user_id
            )

            if not user:
                return _error_response(
                    "User not found",
                    401,
                )

            if not user.is_active:
                return _error_response(
                    "User account is inactive",
                    403,
                )

            request.mobile_user = user

        except Exception as exc:
            current_app.logger.error(
                "Mobile authentication error: %s",
                exc,
            )

            return _error_response(
                "Authentication service unavailable",
                500,
            )

        return func(
            *args,
            **kwargs,
        )

    return wrapper


# =============================================================================
# Health
# =============================================================================

@mobile_bp.get("/health")
def mobile_health():
    """
    Return the health status of the mobile API.
    """
    return _success_response(
        {
            "service": "UBP Mobile API",
            "status": "healthy",
        }
    )


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
    data = _request_json()

    username, error = _required_string(
        data,
        "username",
        "Username is required",
    )

    if error:
        return error

    email, error = _required_string(
        data,
        "email",
        "Email is required",
        lowercase=True,
    )

    if error:
        return error

    password = data.get("password", "")

    if not isinstance(password, str) or not password:
        return _error_response(
            "Password is required",
            400,
        )

    if len(password) < 8:
        return _error_response(
            "Password must contain at least 8 characters",
            400,
        )

    try:
        user_service = _get_user_service()

        user = user_service.create_user(
            username=username,
            email=email,
            password=password,
        )

        if not user:
            return _error_response(
                "Unable to create user",
                400,
            )

        token = _create_access_token(user)

        return _success_response(
            {
                "message": "Registration successful",
                "token": token,
                "user": _serialize_user(user),
            },
            201,
        )

    except Exception as exc:
        current_app.logger.error(
            "Mobile registration error: %s",
            exc,
        )

        return _error_response(
            str(exc),
            400,
        )


@mobile_bp.post("/auth/login")
def mobile_login():
    """
    Authenticate a mobile user.

    Expected JSON:

        {
            "username": "...",
            "password": "..."
        }
    """
    data = _request_json()

    username, error = _required_string(
        data,
        "username",
        "Username is required",
    )

    if error:
        return error

    password = data.get("password", "")

    if not isinstance(password, str) or not password:
        return _error_response(
            "Password is required",
            400,
        )

    try:
        user_service = _get_user_service()

        user = user_service.authenticate(
            username=username,
            password=password,
        )

        if not user:
            return _error_response(
                "Invalid username or password",
                401,
            )

        if not user.is_active:
            return _error_response(
                "User account is inactive",
                403,
            )

        token = _create_access_token(user)

        return _success_response(
            {
                "message": "Login successful",
                "token": token,
                "user": _serialize_user(user),
            }
        )

    except Exception as exc:
        current_app.logger.error(
            "Mobile login error: %s",
            exc,
        )

        return _error_response(
            "Authentication failed",
            401,
        )


@mobile_bp.get("/auth/me")
@mobile_auth_required
def mobile_me():
    """
    Return the currently authenticated mobile user.
    """
    user = request.mobile_user

    return _success_response(
        {
            "user": _serialize_user(
                user,
                include_network=True,
            ),
        }
    )


@mobile_bp.post("/auth/logout")
@mobile_auth_required
def mobile_logout():
    """
    Mobile logout endpoint.

    Mobile access tokens are currently stateless. The client removes its
    stored token after receiving this response.
    """
    return _success_response(
        {
            "message": "Logout successful",
        }
    )


# =============================================================================
# Dashboard
# =============================================================================

@mobile_bp.get("/dashboard/stats")
@mobile_auth_required
def mobile_dashboard_stats():
    """
    Return dashboard statistics for the authenticated user.
    """
    try:
        user = request.mobile_user

        from database.database import get_db_manager
        from database.models import (
            UserTransaction,
            Wallet,
            WalletInspection,
        )
        from uuid import UUID

        db = get_db_manager()

        with db.get_session() as session:
            wallets = (
                session.query(Wallet)
                .filter(
                    Wallet.user_id == user.id,
                    Wallet.is_active == True,
                )
                .all()
            )

            total_wallets = len(wallets)

            blockchain_stats = {
                blockchain: {
                    "wallets": 0,
                    "transactions": 0,
                }
                for blockchain in SUPPORTED_BLOCKCHAINS
            }

            wallet_ids = [
                str(wallet.id)
                for wallet in wallets
            ]

            for wallet in wallets:
                blockchain = (
                    str(wallet.blockchain)
                    .lower()
                )

                if blockchain in blockchain_stats:
                    blockchain_stats[
                        blockchain
                    ]["wallets"] += 1

            transactions = []

            if wallet_ids:
                wallet_uuids = [
                    UUID(wallet_id)
                    for wallet_id in wallet_ids
                ]

                transactions = (
                    session.query(UserTransaction)
                    .filter(
                        UserTransaction.wallet_id.in_(
                            wallet_uuids
                        )
                    )
                    .all()
                )

            total_transactions = len(
                transactions
            )

            for transaction in transactions:
                blockchain = (
                    str(transaction.blockchain)
                    .lower()
                )

                if blockchain in blockchain_stats:
                    blockchain_stats[
                        blockchain
                    ]["transactions"] += 1

            recent_activity = []

            wallet_addresses = [
                wallet.address
                for wallet in wallets
            ]

            if wallet_addresses:
                inspections = (
                    session.query(WalletInspection)
                    .filter(
                        WalletInspection.address.in_(
                            wallet_addresses
                        )
                    )
                    .order_by(
                        WalletInspection.created_at.desc()
                    )
                    .limit(5)
                    .all()
                )

                for inspection in inspections:
                    recent_activity.append(
                        {
                            "type": "wallet_inspection",
                            "blockchain": inspection.blockchain,
                            "address": inspection.address,
                            "amount": None,
                            "created_at": (
                                inspection.created_at.isoformat()
                                if inspection.created_at
                                else None
                            ),
                        }
                    )

            if wallet_ids:
                wallet_uuids = [
                    UUID(wallet_id)
                    for wallet_id in wallet_ids
                ]

                recent_transactions = (
                    session.query(UserTransaction)
                    .filter(
                        UserTransaction.wallet_id.in_(
                            wallet_uuids
                        )
                    )
                    .order_by(
                        UserTransaction.created_at.desc()
                    )
                    .limit(5)
                    .all()
                )

                for transaction in recent_transactions:
                    recent_activity.append(
                        {
                            "type": "transaction",
                            "blockchain": transaction.blockchain,
                            "address": transaction.to_address,
                            "amount": (
                                float(transaction.amount)
                                if transaction.amount
                                else None
                            ),
                            "asset": transaction.asset,
                            "status": transaction.status,
                            "created_at": (
                                transaction.created_at.isoformat()
                                if transaction.created_at
                                else None
                            ),
                        }
                    )

            recent_activity.sort(
                key=lambda item: (
                    item.get("created_at")
                    or ""
                ),
                reverse=True,
            )

            recent_activity = recent_activity[:10]

        return _success_response(
            {
                "data": {
                    "total_wallets": total_wallets,
                    "total_transactions": total_transactions,
                    "by_blockchain": blockchain_stats,
                    "recent_activity": recent_activity,
                },
            }
        )

    except Exception as exc:
        current_app.logger.error(
            "Mobile dashboard error: %s",
            exc,
        )

        return _error_response(
            str(exc),
            500,
        )


# =============================================================================
# Wallet Management
# =============================================================================

@mobile_bp.post("/wallets/create")
@mobile_auth_required
def mobile_create_wallet():
    """
    Create a new wallet for the authenticated user.
    """
    try:
        user = request.mobile_user
        data = _request_json()

        blockchain, error = _required_string(
            data,
            "blockchain",
            "Blockchain is required",
            lowercase=True,
        )

        if error:
            return error

        if blockchain not in SUPPORTED_BLOCKCHAINS:
            return _error_response(
                "Blockchain must be ethereum, bitcoin, or tron",
                400,
            )

        label = str(
            data.get("label", "")
        ).strip()

        if not label:
            label = (
                f"{blockchain.capitalize()} Wallet"
            )

        wallet_service = _get_wallet_service()

        wallet = wallet_service.create_wallet(
            user_id=user.id,
            blockchain=blockchain,
            label=label,
        )

        if not wallet:
            return _error_response(
                "Failed to create wallet",
                500,
            )

        return _success_response(
            {
                "wallet": {
                    "id": str(
                        wallet.get("id")
                    ),
                    "wallet_id": wallet.get(
                        "wallet_id"
                    ),
                    "address": wallet.get(
                        "address"
                    ),
                    "blockchain": wallet.get(
                        "blockchain"
                    ),
                    "network": wallet.get(
                        "network",
                        "mainnet",
                    ),
                    "label": wallet.get(
                        "label"
                    ),
                    "created_at": wallet.get(
                        "created_at"
                    ),
                },
            },
            201,
        )

    except Exception as exc:
        current_app.logger.error(
            "Mobile wallet creation error: %s",
            exc,
        )

        return _error_response(
            str(exc),
            500,
        )


@mobile_bp.get("/wallets")
@mobile_auth_required
def mobile_list_wallets():
    """
    List all wallets for the authenticated user.
    """
    try:
        user = request.mobile_user
        wallet_service = _get_wallet_service()

        wallets = wallet_service.get_user_wallets(
            user.id
        )

        return _success_response(
            {
                "wallets": wallets,
            }
        )

    except Exception as exc:
        current_app.logger.error(
            "Mobile list wallets error: %s",
            exc,
        )

        return _error_response(
            str(exc),
            500,
        )


@mobile_bp.get("/wallets/<wallet_id>/balance")
@mobile_auth_required
def mobile_get_wallet_balance(
    wallet_id: str,
):
    """
    Get the balance for a specific wallet.
    """
    try:
        user = request.mobile_user
        wallet_service = _get_wallet_service()

        wallet, error = _require_owned_wallet(
            wallet_service,
            user.id,
            wallet_id,
        )

        if error:
            return error

        balance = wallet_service.get_wallet_balance(
            wallet_id
        )

        if "error" in balance:
            return _error_response(
                balance["error"],
                400,
            )

        return _success_response(
            {
                "balance": balance,
            }
        )

    except Exception as exc:
        current_app.logger.error(
            "Mobile get balance error: %s",
            exc,
        )

        return _error_response(
            str(exc),
            500,
        )


# =============================================================================
# Wallet Inspection
# =============================================================================

@mobile_bp.get("/wallets/<wallet_id>/inspect")
@mobile_auth_required
def mobile_inspect_wallet(
    wallet_id: str,
):
    """
    Inspect a wallet with detailed information including token holdings.
    """
    try:
        user = request.mobile_user
        wallet_service = _get_wallet_service()

        wallet, error = _require_owned_wallet(
            wallet_service,
            user.id,
            wallet_id,
        )

        if error:
            return error

        report = wallet_service.get_wallet_report(
            wallet_id
        )

        if "error" in report:
            return _error_response(
                report["error"],
                400,
            )

        report.update(
            {
                "wallet_id": wallet.get(
                    "wallet_id"
                ),
                "label": wallet.get(
                    "label"
                ),
                "blockchain": wallet.get(
                    "blockchain"
                ),
                "network": wallet.get(
                    "network",
                    "mainnet",
                ),
                "created_at": wallet.get(
                    "created_at"
                ),
            }
        )

        return _success_response(
            {
                "wallet": report,
            }
        )

    except Exception as exc:
        current_app.logger.error(
            "Mobile inspect wallet error: %s",
            exc,
        )

        return _error_response(
            str(exc),
            500,
        )


# =============================================================================
# Transaction Management
# =============================================================================

@mobile_bp.post("/wallets/<wallet_id>/send")
@mobile_auth_required
def mobile_send_transaction(
    wallet_id: str,
):
    """
    Send a transaction from a user's wallet.
    """
    try:
        user = request.mobile_user
        data = _request_json()

        to_address, error = _required_string(
            data,
            "to_address",
            "Recipient address is required",
        )

        if error:
            return error

        amount_value = data.get("amount")

        if amount_value is None:
            return _error_response(
                "Amount is required",
                400,
            )

        try:
            amount = float(amount_value)
        except (
            ValueError,
            TypeError,
        ):
            return _error_response(
                "Amount must be a valid number",
                400,
            )

        if amount <= 0:
            return _error_response(
                "Amount must be greater than 0",
                400,
            )

        wallet_service = _get_wallet_service()

        wallet, error = _require_owned_wallet(
            wallet_service,
            user.id,
            wallet_id,
        )

        if error:
            return error

        result = wallet_service.send_transaction(
            wallet_id=wallet_id,
            to_address=to_address,
            amount=amount,
        )

        if "error" in result:
            return _error_response(
                result["error"],
                400,
            )

        return _success_response(
            {
                "transaction": {
                    "tx_hash": result.get(
                        "tx_hash"
                    ),
                    "from": result.get(
                        "from"
                    ),
                    "to": result.get(
                        "to"
                    ),
                    "amount": result.get(
                        "amount"
                    ),
                    "asset": result.get(
                        "asset",
                        "ETH",
                    ),
                    "fee": result.get(
                        "fee"
                    ),
                    "status": result.get(
                        "status",
                        "pending",
                    ),
                },
            }
        )

    except Exception as exc:
        current_app.logger.error(
            "Mobile send transaction error: %s",
            exc,
        )

        return _error_response(
            str(exc),
            500,
        )


# =============================================================================
# Transaction History
# =============================================================================

@mobile_bp.get("/wallets/<wallet_id>/transactions")
@mobile_auth_required
def mobile_get_transactions(
    wallet_id: str,
):
    """
    Get transaction history for a wallet.
    """
    try:
        user = request.mobile_user

        limit, offset, pagination_error = (
            _parse_pagination()
        )

        if pagination_error:
            return _error_response(
                pagination_error,
                400,
            )

        wallet_service = _get_wallet_service()

        wallet, error = _require_owned_wallet(
            wallet_service,
            user.id,
            wallet_id,
        )

        if error:
            return error

        result = (
            wallet_service.get_transaction_history(
                wallet_id,
                limit,
                offset,
            )
        )

        if "error" in result:
            return _error_response(
                result["error"],
                400,
            )

        return _success_response(
            {
                "transactions": result.get(
                    "transactions",
                    [],
                ),
                "total": result.get(
                    "total",
                    0,
                ),
                "limit": result.get(
                    "limit",
                    limit,
                ),
                "offset": result.get(
                    "offset",
                    offset,
                ),
                "total_pages": result.get(
                    "total_pages",
                    1,
                ),
            }
        )

    except Exception as exc:
        current_app.logger.error(
            "Mobile get transactions error: %s",
            exc,
        )

        return _error_response(
            str(exc),
            500,
        )


# =============================================================================
# Token Holdings
# =============================================================================

@mobile_bp.get("/wallets/<wallet_id>/tokens")
@mobile_auth_required
def mobile_get_tokens(
    wallet_id: str,
):
    """
    Get token holdings for a wallet.
    """
    try:
        user = request.mobile_user
        wallet_service = _get_wallet_service()

        wallet, error = _require_owned_wallet(
            wallet_service,
            user.id,
            wallet_id,
        )

        if error:
            return error

        result = wallet_service.get_token_holdings(
            wallet_id
        )

        if "error" in result:
            return _error_response(
                result["error"],
                400,
            )

        return _success_response(
            {
                "tokens": result.get(
                    "tokens",
                    [],
                ),
                "blockchain": result.get(
                    "blockchain"
                ),
                "address": result.get(
                    "address"
                ),
                "total_tokens": result.get(
                    "total_tokens",
                    0,
                ),
            }
        )

    except Exception as exc:
        current_app.logger.error(
            "Mobile get tokens error: %s",
            exc,
        )

        return _error_response(
            str(exc),
            500,
        )


# =============================================================================
# End of Module
# =============================================================================