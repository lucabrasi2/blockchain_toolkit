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
This module provides the HTTP boundary for mobile clients.

It must NOT contain:
    - blockchain provider logic
    - wallet cryptographic logic
    - transaction signing logic
    - database business logic

Those responsibilities remain in the existing UBP services and controllers.

Current Scope
-------------
The initial implementation provides a health endpoint so that the mobile
API boundary can be registered and tested independently before authentication,
wallet, and blockchain endpoints are added.

Blueprint Prefix
----------------
/api/mobile
===============================================================================
"""

from flask import Blueprint, jsonify


# =============================================================================
# Mobile API Blueprint
# =============================================================================

mobile_bp = Blueprint(
    "mobile",
    __name__,
    url_prefix="/api/mobile",
)


# =============================================================================
# Health
# =============================================================================

@mobile_bp.get("/health")
def mobile_health():
    """
    Return the health status of the mobile API.

    This endpoint is intentionally independent of authentication and database
    state. Its purpose is to verify that the mobile API blueprint is loaded
    and reachable by the mobile client.
    """
    return jsonify(
        {
            "success": True,
            "service": "UBP Mobile API",
            "status": "healthy",
        }
    ), 200


# =============================================================================
# Future Mobile API Sections
# =============================================================================
#
# Authentication:
#   POST /api/mobile/auth/login
#   POST /api/mobile/auth/register
#   POST /api/mobile/auth/logout
#   GET  /api/mobile/auth/me
#
# Dashboard:
#   GET /api/mobile/dashboard/stats
#
# Wallets:
#   GET  /api/mobile/wallets
#   POST /api/mobile/wallets
#   GET  /api/mobile/wallets/<wallet_id>
#
# Transactions:
#   GET  /api/mobile/transactions
#   POST /api/mobile/transactions
#
# Blockchain:
#   GET /api/mobile/ethereum/...
#   GET /api/mobile/bitcoin/...
#   GET /api/mobile/tron/...
#
# These endpoints will be implemented through the existing UBP services
# and controllers rather than duplicating business logic in this module.
# =============================================================================
