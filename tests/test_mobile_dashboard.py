"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
tests.test_mobile_dashboard

Purpose
-------
Tests for the mobile dashboard API endpoint.

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

import json
import uuid
import time
import pytest
from flask import Flask
from flask.testing import FlaskClient

from api.mobile import mobile_bp
from services.user_service import UserService
from services.wallet_service import WalletService
from database.database import get_db_manager
from database.models import User, Wallet


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def app() -> Flask:
    """Create a test Flask application."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret-key"
    app.config["TESTING"] = True
    app.register_blueprint(mobile_bp)
    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def test_user() -> User:
    """Create a test user with unique credentials."""
    user_service = UserService()
    
    # Generate unique credentials using timestamp
    timestamp = int(time.time() * 1000)
    username = f"testmobile_{timestamp}"
    email = f"testmobile_{timestamp}@example.com"
    
    user = user_service.create_user(
        username=username,
        email=email,
        password="password123"
    )
    
    # If user already exists, try with a different ID
    if user is None:
        import random
        suffix = random.randint(10000, 99999)
        username = f"testmobile_{timestamp}_{suffix}"
        email = f"testmobile_{timestamp}_{suffix}@example.com"
        user = user_service.create_user(
            username=username,
            email=email,
            password="password123"
        )
    
    return user


@pytest.fixture
def auth_token(client: FlaskClient, test_user: User) -> str:
    """Get an authentication token for the test user."""
    if test_user is None:
        pytest.fail("Test user could not be created")
    
    response = client.post(
        "/api/mobile/auth/login",
        json={
            "username": test_user.username,
            "password": "password123"
        }
    )
    data = json.loads(response.data)
    return data.get("token")


@pytest.fixture
def test_wallet(test_user: User) -> Wallet:
    """Create a test wallet for the user."""
    if test_user is None:
        pytest.fail("Test user could not be created")
    
    wallet_service = WalletService()
    wallet = wallet_service.create_wallet(
        user_id=test_user.id,
        blockchain="ethereum",
        label="Test ETH Wallet"
    )
    return wallet


# ============================================================================
# Tests
# ============================================================================

def test_dashboard_stats_requires_auth(client: FlaskClient):
    """
    Verify that the dashboard endpoint requires authentication.
    """
    response = client.get("/api/mobile/dashboard/stats")
    data = json.loads(response.data)

    assert response.status_code == 401
    assert data.get("success") is False
    assert "Missing Bearer token" in data.get("error", "")


def test_dashboard_stats_invalid_token(client: FlaskClient):
    """
    Verify that an invalid token is rejected.
    """
    response = client.get(
        "/api/mobile/dashboard/stats",
        headers={"Authorization": "Bearer invalid-token"}
    )
    data = json.loads(response.data)

    assert response.status_code == 401
    assert data.get("success") is False
    assert "Invalid or expired access token" in data.get("error", "")


def test_dashboard_stats_success(
    client: FlaskClient,
    auth_token: str,
    test_user: User,
    test_wallet: Wallet
):
    """
    Verify that the dashboard endpoint returns statistics successfully.
    """
    if test_user is None or auth_token is None:
        pytest.fail("Test user or token could not be created")

    response = client.get(
        "/api/mobile/dashboard/stats",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200

    data = json.loads(response.data)
    assert data.get("success") is True

    dashboard_data = data.get("data", {})
    
    # Check total wallets
    assert "total_wallets" in dashboard_data
    assert dashboard_data["total_wallets"] >= 1

    # Check total transactions
    assert "total_transactions" in dashboard_data
    assert isinstance(dashboard_data["total_transactions"], int)

    # Check blockchain breakdown
    assert "by_blockchain" in dashboard_data
    
    blockchain_stats = dashboard_data["by_blockchain"]
    assert "ethereum" in blockchain_stats
    assert "bitcoin" in blockchain_stats
    assert "tron" in blockchain_stats

    # Check each blockchain has wallet and transaction counts
    for chain in ["ethereum", "bitcoin", "tron"]:
        assert "wallets" in blockchain_stats[chain]
        assert "transactions" in blockchain_stats[chain]
        assert isinstance(blockchain_stats[chain]["wallets"], int)
        assert isinstance(blockchain_stats[chain]["transactions"], int)

    # Check recent activity
    assert "recent_activity" in dashboard_data
    assert isinstance(dashboard_data["recent_activity"], list)


def test_dashboard_stats_response_structure(
    client: FlaskClient,
    auth_token: str
):
    """
    Verify the complete response structure of the dashboard endpoint.
    """
    if auth_token is None:
        pytest.fail("Auth token could not be created")

    response = client.get(
        "/api/mobile/dashboard/stats",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200

    data = json.loads(response.data)
    assert data.get("success") is True

    dashboard_data = data.get("data", {})
    
    # Expected top-level fields
    expected_fields = [
        "total_wallets",
        "total_transactions",
        "by_blockchain",
        "recent_activity"
    ]
    
    for field in expected_fields:
        assert field in dashboard_data, f"Missing field: {field}"

    # Expected blockchain fields
    expected_chains = ["ethereum", "bitcoin", "tron"]
    for chain in expected_chains:
        assert chain in dashboard_data["by_blockchain"]

    # Activity items should have specific fields
    for activity in dashboard_data["recent_activity"]:
        assert "type" in activity
        assert "blockchain" in activity
        assert "created_at" in activity
        assert activity["type"] in ["wallet_inspection", "transaction"]


def test_dashboard_stats_handles_no_wallets(
    client: FlaskClient
):
    """
    Verify that the dashboard endpoint handles the case where a user has no wallets.
    """
    # Create a user with no wallets
    user_service = UserService()
    
    timestamp = int(time.time() * 1000)
    username = f"nowallets_{timestamp}"
    email = f"nowallets_{timestamp}@example.com"
    
    user = user_service.create_user(
        username=username,
        email=email,
        password="password123"
    )
    
    if user is None:
        import random
        suffix = random.randint(10000, 99999)
        username = f"nowallets_{timestamp}_{suffix}"
        email = f"nowallets_{timestamp}_{suffix}@example.com"
        user = user_service.create_user(
            username=username,
            email=email,
            password="password123"
        )
    
    assert user is not None, "Test user could not be created"

    # Login to get token
    response = client.post(
        "/api/mobile/auth/login",
        json={
            "username": user.username,
            "password": "password123"
        }
    )
    login_data = json.loads(response.data)
    token = login_data.get("token")
    
    assert token is not None, "Auth token could not be obtained"

    response = client.get(
        "/api/mobile/dashboard/stats",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = json.loads(response.data)
    assert data.get("success") is True

    dashboard_data = data.get("data", {})
    assert dashboard_data["total_wallets"] == 0
    assert dashboard_data["total_transactions"] == 0

    for chain in ["ethereum", "bitcoin", "tron"]:
        assert dashboard_data["by_blockchain"][chain]["wallets"] == 0
        assert dashboard_data["by_blockchain"][chain]["transactions"] == 0


def test_dashboard_stats_error_handling(client: FlaskClient):
    """
    Verify error handling for the dashboard endpoint.
    """
    # Test with invalid token
    response = client.get(
        "/api/mobile/dashboard/stats",
        headers={"Authorization": "Bearer malformed-token"}
    )

    assert response.status_code == 401
    
    data = json.loads(response.data)
    assert data.get("success") is False