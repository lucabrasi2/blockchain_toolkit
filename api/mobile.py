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
# End of Module
# =============================================================================
