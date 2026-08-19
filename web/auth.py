"""
Web Authentication Routes for UBP Blockchain Toolkit.

Provides:
- User registration
- Login/logout
- Profile management
- Password reset
- API key management
- Two-factor authentication
- Flask-Login integration
- JWT authentication
"""

import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, Optional
from urllib.parse import urljoin, urlparse

import bcrypt
import jwt
import pyotp
import qrcode
from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from io import BytesIO
from werkzeug.utils import secure_filename

from core.logger import get_logger


logger = get_logger(__name__)

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)

login_manager = LoginManager()

# =============================================================================
# Configuration
# =============================================================================

JWT_ALGORITHM = "HS256"

DEFAULT_JWT_EXPIRY_HOURS = 24

MIN_PASSWORD_LENGTH = 8

API_KEY_PREFIX = "ubp_"
API_KEY_BYTES = 32

SUPPORTED_ROLES = {
    "user",
    "admin",
    "viewer",
    "api",
}


# =============================================================================
# User Model
# =============================================================================

class User(UserMixin):
    """Flask-Login compatible user representation."""

    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        role: str = "user",
        is_active: bool = True,
        is_verified: bool = False,
        two_factor_enabled: bool = False,
    ):
        self.id = str(user_id)
        self.username = username
        self.email = email
        self.role = role
        self.is_active = bool(is_active)
        self.is_verified = bool(is_verified)
        self.two_factor_enabled = bool(two_factor_enabled)

    def get_id(self) -> str:
        """Return the user identifier required by Flask-Login."""
        return str(self.id)


# =============================================================================
# User Manager
# =============================================================================

class UserManager:
    """Manage web authentication users using the existing SQLite database."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = (
            db_path
            or current_app.config.get("DATABASE_PATH")
            or "ubp.db"
        )

        self._initialize_database()

    # =========================================================================
    # Internal Database Helpers
    # =========================================================================

    def _get_connection(self) -> sqlite3.Connection:
        """
        Create a configured SQLite connection.

        Row objects allow callers to access columns by name while preserving
        compatibility with the existing SQLite-backed authentication layer.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        # Enforce foreign-key constraints for this connection.
        conn.execute("PRAGMA foreign_keys = ON")

        return conn

    def _initialize_database(self) -> None:
        """Initialize required authentication tables."""
        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    api_key TEXT UNIQUE,
                    is_active INTEGER DEFAULT 1,
                    is_verified INTEGER DEFAULT 0,
                    two_factor_secret TEXT,
                    two_factor_enabled INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    last_login TEXT
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    key_hash TEXT NOT NULL,
                    key_prefix TEXT NOT NULL,
                    name TEXT,
                    created_at TEXT NOT NULL,
                    last_used TEXT,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    token_hash TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    used INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """
            )

            conn.commit()

        except Exception:
            conn.rollback()
            logger.exception("Failed to initialize authentication database")
            raise

        finally:
            conn.close()

    # =========================================================================
    # Input Helpers
    # =========================================================================

    @staticmethod
    def _normalize_username(username: Any) -> Optional[str]:
        """Normalize a username."""
        if not isinstance(username, str):
            return None

        username = username.strip()

        if not username:
            return None

        return username

    @staticmethod
    def _normalize_email(email: Any) -> Optional[str]:
        """Normalize an email address."""
        if not isinstance(email, str):
            return None

        email = email.strip().lower()

        if not email:
            return None

        return email

    @staticmethod
    def _validate_password(password: Any) -> bool:
        """Validate the minimum password requirement."""
        return (
            isinstance(password, str)
            and len(password) >= MIN_PASSWORD_LENGTH
        )

    @staticmethod
    def _normalize_role(role: Any) -> Optional[str]:
        """Validate and normalize a user role."""
        if not isinstance(role, str):
            return None

        role = role.strip().lower()

        if role not in SUPPORTED_ROLES:
            return None

        return role

    @staticmethod
    def _hash_api_key(api_key: str) -> str:
        """Return a SHA-256 hash of an API key."""
        return hashlib.sha256(
            api_key.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _generate_api_key() -> str:
        """Generate a cryptographically secure UBP API key."""
        return (
            API_KEY_PREFIX
            + secrets.token_hex(API_KEY_BYTES)
        )

    # =========================================================================
    # User Creation
    # =========================================================================

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "user",
    ) -> Optional[User]:
        """
        Create a new authentication user.

        Existing return behavior is preserved:
        - User object on success
        - None on failure
        """
        username = self._normalize_username(username)
        email = self._normalize_email(email)
        role = self._normalize_role(role)

        if not username:
            logger.warning("User creation rejected: invalid username")
            return None

        if not email:
            logger.warning("User creation rejected: invalid email")
            return None

        if not self._validate_password(password):
            logger.warning(
                "User creation rejected: password below minimum length"
            )
            return None

        if not role:
            logger.warning("User creation rejected: invalid role")
            return None

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE username = ? OR email = ?
                LIMIT 1
                """,
                (username, email),
            )

            if cursor.fetchone():
                logger.warning(
                    "User already exists: username=%s email=%s",
                    username,
                    email,
                )
                return None

            user_id = secrets.token_hex(16)

            password_hash = bcrypt.generate_password_hash(
                password
            ).decode("utf-8")

            api_key = self._generate_api_key()

            now = datetime.utcnow().isoformat()

            cursor.execute(
                """
                INSERT INTO users (
                    id,
                    username,
                    email,
                    password_hash,
                    role,
                    api_key,
                    is_active,
                    is_verified,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, 1, 0, ?)
                """,
                (
                    user_id,
                    username,
                    email,
                    password_hash,
                    role,
                    api_key,
                    now,
                ),
            )

            conn.commit()

            logger.info(
                "User created successfully: %s",
                username,
            )

            return User(
                user_id=user_id,
                username=username,
                email=email,
                role=role,
                is_active=True,
                is_verified=False,
                two_factor_enabled=False,
            )

        except sqlite3.IntegrityError:
            conn.rollback()

            logger.warning(
                "User creation failed due to duplicate data: %s",
                username,
            )

            return None

        except Exception:
            conn.rollback()

            logger.exception(
                "Unexpected error creating user: %s",
                username,
            )

            return None

        finally:
            conn.close()

    # =========================================================================
    # User Lookup
    # =========================================================================

    def get_user_by_id(
        self,
        user_id: str,
    ) -> Optional[User]:
        """Get a user by ID."""
        if not user_id:
            return None

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    email,
                    role,
                    is_active,
                    is_verified,
                    two_factor_enabled
                FROM users
                WHERE id = ?
                LIMIT 1
                """,
                (str(user_id),),
            )

            row = cursor.fetchone()

            if not row:
                return None

            return User(
                user_id=row["id"],
                username=row["username"],
                email=row["email"],
                role=row["role"] or "user",
                is_active=bool(row["is_active"]),
                is_verified=bool(row["is_verified"]),
                two_factor_enabled=bool(
                    row["two_factor_enabled"]
                ),
            )

        except Exception:
            logger.exception(
                "Error getting user by ID: %s",
                user_id,
            )
            return None

        finally:
            conn.close()

    def get_user_by_username(
        self,
        username: str,
    ) -> Optional[User]:
        """Get a user by username."""
        username = self._normalize_username(username)

        if not username:
            return None

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    email,
                    role,
                    is_active,
                    is_verified,
                    two_factor_enabled
                FROM users
                WHERE username = ?
                LIMIT 1
                """,
                (username,),
            )

            row = cursor.fetchone()

            if not row:
                return None

            return User(
                user_id=row["id"],
                username=row["username"],
                email=row["email"],
                role=row["role"] or "user",
                is_active=bool(row["is_active"]),
                is_verified=bool(row["is_verified"]),
                two_factor_enabled=bool(
                    row["two_factor_enabled"]
                ),
            )

        except Exception:
            logger.exception(
                "Error getting user by username: %s",
                username,
            )
            return None

        finally:
            conn.close()

    def get_user_by_email(
        self,
        email: str,
    ) -> Optional[User]:
        """Get a user by email address."""
        email = self._normalize_email(email)

        if not email:
            return None

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    email,
                    role,
                    is_active,
                    is_verified,
                    two_factor_enabled
                FROM users
                WHERE email = ?
                LIMIT 1
                """,
                (email,),
            )

            row = cursor.fetchone()

            if not row:
                return None

            return User(
                user_id=row["id"],
                username=row["username"],
                email=row["email"],
                role=row["role"] or "user",
                is_active=bool(row["is_active"]),
                is_verified=bool(row["is_verified"]),
                two_factor_enabled=bool(
                    row["two_factor_enabled"]
                ),
            )

        except Exception:
            logger.exception(
                "Error getting user by email: %s",
                email,
            )
            return None

        finally:
            conn.close()

    # =========================================================================
    # Authentication
    # =========================================================================

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> Optional[User]:
        """
        Authenticate a user.

        Returns None for:
        - invalid credentials
        - inactive accounts
        - invalid input
        """
        username = self._normalize_username(username)

        if not username or not isinstance(password, str):
            return None

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    email,
                    password_hash,
                    role,
                    is_active,
                    is_verified,
                    two_factor_enabled
                FROM users
                WHERE username = ?
                LIMIT 1
                """,
                (username,),
            )

            row = cursor.fetchone()

            if not row:
                logger.warning(
                    "Authentication failed: user not found: %s",
                    username,
                )
                return None

            if not bool(row["is_active"]):
                logger.warning(
                    "Authentication failed: inactive user: %s",
                    username,
                )
                return None

            try:
                password_valid = bcrypt.check_password_hash(
                    row["password_hash"],
                    password,
                )
            except (ValueError, TypeError):
                logger.warning(
                    "Authentication failed: invalid password hash for %s",
                    username,
                )
                return None

            if not password_valid:
                logger.warning(
                    "Authentication failed: invalid password for %s",
                    username,
                )
                return None

            now = datetime.utcnow().isoformat()

            cursor.execute(
                """
                UPDATE users
                SET last_login = ?
                WHERE id = ?
                """,
                (now, row["id"]),
            )

            conn.commit()

            logger.info(
                "User authenticated successfully: %s",
                username,
            )

            return User(
                user_id=row["id"],
                username=row["username"],
                email=row["email"],
                role=row["role"] or "user",
                is_active=True,
                is_verified=bool(row["is_verified"]),
                two_factor_enabled=bool(
                    row["two_factor_enabled"]
                ),
            )

        except Exception:
            conn.rollback()

            logger.exception(
                "Authentication error for user: %s",
                username,
            )

            return None

        finally:
            conn.close()

    # =========================================================================
    # API-Key Management
    # =========================================================================

    def get_user_by_api_key(
        self,
        api_key: str,
    ) -> Optional[User]:
        """Get an active user by API key."""
        if not isinstance(api_key, str):
            return None

        api_key = api_key.strip()

        if not api_key:
            return None

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    email,
                    role,
                    is_active,
                    is_verified,
                    two_factor_enabled
                FROM users
                WHERE api_key = ?
                  AND is_active = 1
                LIMIT 1
                """,
                (api_key,),
            )

            row = cursor.fetchone()

            if not row:
                return None

            user = User(
                user_id=row["id"],
                username=row["username"],
                email=row["email"],
                role=row["role"] or "user",
                is_active=True,
                is_verified=bool(row["is_verified"]),
                two_factor_enabled=bool(
                    row["two_factor_enabled"]
                ),
            )

            return user

        except Exception:
            logger.exception("Error authenticating API key")
            return None

        finally:
            conn.close()

    def create_api_key(
        self,
        user_id: str,
        name: str = "Default",
    ) -> Optional[str]:
        """
        Create an API key for a user.

        The plaintext key is returned only at creation time.
        """
        if not user_id:
            return None

        name = (
            name.strip()
            if isinstance(name, str) and name.strip()
            else "Default"
        )

        api_key = self._generate_api_key()
        key_hash = self._hash_api_key(api_key)
        key_prefix = api_key[:12]

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE id = ?
                  AND is_active = 1
                LIMIT 1
                """,
                (str(user_id),),
            )

            if not cursor.fetchone():
                return None

            cursor.execute(
                """
                INSERT INTO api_keys (
                    user_id,
                    key_hash,
                    key_prefix,
                    name,
                    created_at,
                    is_active
                )
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (
                    str(user_id),
                    key_hash,
                    key_prefix,
                    name,
                    datetime.utcnow().isoformat(),
                ),
            )

            conn.commit()

            logger.info(
                "API key created for user: %s",
                user_id,
            )

            return api_key

        except sqlite3.IntegrityError:
            conn.rollback()
            logger.warning(
                "Could not create API key for user: %s",
                user_id,
            )
            return None

        except Exception:
            conn.rollback()
            logger.exception(
                "Error creating API key for user: %s",
                user_id,
            )
            return None

        finally:
            conn.close()
        # =========================================================================
    # API-Key Operations
    # =========================================================================

    def list_api_keys(
        self,
        user_id: str,
    ) -> list:
        """Return active API keys belonging to a user."""
        if not user_id:
            return []

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    key_prefix,
                    name,
                    created_at,
                    last_used,
                    is_active
                FROM api_keys
                WHERE user_id = ?
                  AND is_active = 1
                ORDER BY created_at DESC
                """,
                (str(user_id),),
            )

            return [dict(row) for row in cursor.fetchall()]

        except Exception:
            logger.exception(
                "Error listing API keys for user: %s",
                user_id,
            )
            return []

        finally:
            conn.close()

    def revoke_api_key(
        self,
        key_id: int,
        user_id: str,
    ) -> bool:
        """Revoke an API key belonging to a specific user."""
        if not key_id or not user_id:
            return False

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE api_keys
                SET is_active = 0
                WHERE id = ?
                  AND user_id = ?
                  AND is_active = 1
                """,
                (key_id, str(user_id)),
            )

            changed = cursor.rowcount > 0
            conn.commit()

            if changed:
                logger.info(
                    "API key %s revoked for user %s",
                    key_id,
                    user_id,
                )

            return changed

        except Exception:
            conn.rollback()

            logger.exception(
                "Error revoking API key %s",
                key_id,
            )

            return False

        finally:
            conn.close()

    def update_api_key_usage(
        self,
        api_key: str,
    ) -> None:
        """Update the last-used timestamp for an API key."""
        if not isinstance(api_key, str):
            return

        api_key = api_key.strip()

        if not api_key:
            return

        key_hash = self._hash_api_key(api_key)
        now = datetime.utcnow().isoformat()

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE api_keys
                SET last_used = ?
                WHERE key_hash = ?
                  AND is_active = 1
                """,
                (now, key_hash),
            )

            conn.commit()

        except Exception:
            conn.rollback()

            logger.exception(
                "Error updating API key usage"
            )

        finally:
            conn.close()

    # =========================================================================
    # Password Reset
    # =========================================================================

    def create_password_reset_token(
        self,
        user_id: str,
        expiry_minutes: int = 60,
    ) -> Optional[str]:
        """
        Create a password-reset token.

        Only the hash is stored in the database. The plaintext token is
        returned to the caller.
        """
        if not user_id:
            return None

        try:
            expiry_minutes = max(
                5,
                min(int(expiry_minutes), 24 * 60),
            )
        except (TypeError, ValueError):
            expiry_minutes = 60

        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

        now = datetime.utcnow()
        expires_at = (
            now + timedelta(minutes=expiry_minutes)
        ).isoformat()

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE id = ?
                  AND is_active = 1
                LIMIT 1
                """,
                (str(user_id),),
            )

            if not cursor.fetchone():
                return None

            # Invalidate outstanding tokens for this user.
            cursor.execute(
                """
                UPDATE password_reset_tokens
                SET used = 1
                WHERE user_id = ?
                  AND used = 0
                """,
                (str(user_id),),
            )

            cursor.execute(
                """
                INSERT INTO password_reset_tokens (
                    user_id,
                    token_hash,
                    expires_at,
                    used,
                    created_at
                )
                VALUES (?, ?, ?, 0, ?)
                """,
                (
                    str(user_id),
                    token_hash,
                    expires_at,
                    now.isoformat(),
                ),
            )

            conn.commit()

            logger.info(
                "Password reset token created for user: %s",
                user_id,
            )

            return token

        except Exception:
            conn.rollback()

            logger.exception(
                "Error creating password reset token"
            )

            return None

        finally:
            conn.close()

    def verify_password_reset_token(
        self,
        token: str,
    ) -> Optional[str]:
        """
        Verify a password-reset token.

        Returns the associated user ID when valid.
        """
        if not isinstance(token, str):
            return None

        token = token.strip()

        if not token:
            return None

        token_hash = hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    user_id,
                    expires_at
                FROM password_reset_tokens
                WHERE token_hash = ?
                  AND used = 0
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (token_hash,),
            )

            row = cursor.fetchone()

            if not row:
                return None

            try:
                expires_at = datetime.fromisoformat(
                    row["expires_at"]
                )
            except (TypeError, ValueError):
                logger.warning(
                    "Invalid password-reset expiry value"
                )
                return None

            if expires_at <= datetime.utcnow():
                return None

            return str(row["user_id"])

        except Exception:
            logger.exception(
                "Error verifying password reset token"
            )
            return None

        finally:
            conn.close()

    def consume_password_reset_token(
        self,
        token: str,
    ) -> Optional[str]:
        """
        Atomically consume a valid password-reset token.

        Returns the user ID if the token was valid and consumed.
        """
        if not isinstance(token, str):
            return None

        token = token.strip()

        if not token:
            return None

        token_hash = hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    user_id,
                    expires_at
                FROM password_reset_tokens
                WHERE token_hash = ?
                  AND used = 0
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (token_hash,),
            )

            row = cursor.fetchone()

            if not row:
                return None

            try:
                expires_at = datetime.fromisoformat(
                    row["expires_at"]
                )
            except (TypeError, ValueError):
                return None

            if expires_at <= datetime.utcnow():
                return None

            cursor.execute(
                """
                UPDATE password_reset_tokens
                SET used = 1
                WHERE id = ?
                  AND used = 0
                """,
                (row["id"],),
            )

            if cursor.rowcount != 1:
                conn.rollback()
                return None

            conn.commit()

            return str(row["user_id"])

        except Exception:
            conn.rollback()

            logger.exception(
                "Error consuming password reset token"
            )

            return None

        finally:
            conn.close()

    # =========================================================================
    # Password Management
    # =========================================================================

    def update_password(
        self,
        user_id: str,
        new_password: str,
    ) -> bool:
        """Update a user's password."""
        if not user_id:
            return False

        if not self._validate_password(new_password):
            return False

        password_hash = bcrypt.generate_password_hash(
            new_password
        ).decode("utf-8")

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE users
                SET password_hash = ?
                WHERE id = ?
                  AND is_active = 1
                """,
                (
                    password_hash,
                    str(user_id),
                ),
            )

            changed = cursor.rowcount > 0

            if changed:
                # Invalidate existing password-reset tokens.
                cursor.execute(
                    """
                    UPDATE password_reset_tokens
                    SET used = 1
                    WHERE user_id = ?
                      AND used = 0
                    """,
                    (str(user_id),),
                )

            conn.commit()

            if changed:
                logger.info(
                    "Password updated for user: %s",
                    user_id,
                )

            return changed

        except Exception:
            conn.rollback()

            logger.exception(
                "Error updating password for user: %s",
                user_id,
            )

            return False

        finally:
            conn.close()

    # =========================================================================
    # Two-Factor Authentication
    # =========================================================================

    def setup_2fa(
        self,
        user_id: str,
    ) -> Optional[str]:
        """
        Generate and store a TOTP secret.

        Returns the secret so the caller can construct the provisioning URI.
        """
        if not user_id:
            return None

        secret = pyotp.random_base32()

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE users
                SET two_factor_secret = ?,
                    two_factor_enabled = 0
                WHERE id = ?
                  AND is_active = 1
                """,
                (
                    secret,
                    str(user_id),
                ),
            )

            changed = cursor.rowcount > 0
            conn.commit()

            if not changed:
                return None

            logger.info(
                "2FA secret generated for user: %s",
                user_id,
            )

            return secret

        except Exception:
            conn.rollback()

            logger.exception(
                "Error setting up 2FA for user: %s",
                user_id,
            )

            return None

        finally:
            conn.close()

    def verify_2fa(
        self,
        user_id: str,
        code: str,
    ) -> bool:
        """Verify and enable TOTP-based two-factor authentication."""
        if not user_id:
            return False

        if not isinstance(code, str):
            return False

        code = code.strip()

        if not code or not code.isdigit():
            return False

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT two_factor_secret
                FROM users
                WHERE id = ?
                  AND is_active = 1
                LIMIT 1
                """,
                (str(user_id),),
            )

            row = cursor.fetchone()

            if not row or not row["two_factor_secret"]:
                return False

            totp = pyotp.TOTP(
                row["two_factor_secret"]
            )

            if not totp.verify(code, valid_window=1):
                return False

            cursor.execute(
                """
                UPDATE users
                SET two_factor_enabled = 1
                WHERE id = ?
                """,
                (str(user_id),),
            )

            conn.commit()

            logger.info(
                "2FA enabled for user: %s",
                user_id,
            )

            return True

        except Exception:
            conn.rollback()

            logger.exception(
                "Error verifying 2FA for user: %s",
                user_id,
            )

            return False

        finally:
            conn.close()

    def disable_2fa(
        self,
        user_id: str,
    ) -> bool:
        """Disable two-factor authentication."""
        if not user_id:
            return False

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE users
                SET two_factor_enabled = 0,
                    two_factor_secret = NULL
                WHERE id = ?
                """,
                (str(user_id),),
            )

            changed = cursor.rowcount > 0
            conn.commit()

            if changed:
                logger.info(
                    "2FA disabled for user: %s",
                    user_id,
                )

            return changed

        except Exception:
            conn.rollback()

            logger.exception(
                "Error disabling 2FA for user: %s",
                user_id,
            )

            return False

        finally:
            conn.close()

    def get_2fa_secret(
        self,
        user_id: str,
    ) -> Optional[str]:
        """Get a user's configured 2FA secret."""
        if not user_id:
            return None

        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT two_factor_secret
                FROM users
                WHERE id = ?
                  AND is_active = 1
                LIMIT 1
                """,
                (str(user_id),),
            )

            row = cursor.fetchone()

            if not row:
                return None

            return row["two_factor_secret"]

        except Exception:
            logger.exception(
                "Error getting 2FA secret for user: %s",
                user_id,
            )
            return None

        finally:
            conn.close()

    # =========================================================================
    # JWT Helpers
    # =========================================================================

    @staticmethod
    def _get_jwt_secret() -> Optional[str]:
        """Get the configured JWT signing secret."""
        secret = current_app.config.get("JWT_SECRET_KEY")

        if not secret:
            secret = current_app.config.get("SECRET_KEY")

        if not secret:
            logger.error(
                "No JWT signing secret configured"
            )
            return None

        return str(secret)

    def create_jwt(
        self,
        user: User,
        expires_hours: int = DEFAULT_JWT_EXPIRY_HOURS,
    ) -> Optional[str]:
        """Create a signed JWT for a user."""
        if not user:
            return None

        secret = self._get_jwt_secret()

        if not secret:
            return None

        try:
            expires_hours = max(
                1,
                min(int(expires_hours), 24 * 30),
            )
        except (TypeError, ValueError):
            expires_hours = DEFAULT_JWT_EXPIRY_HOURS

        now = datetime.utcnow()
        expires_at = now + timedelta(
            hours=expires_hours
        )

        payload = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
            "iat": now,
            "exp": expires_at,
        }

        try:
            return jwt.encode(
                payload,
                secret,
                algorithm=JWT_ALGORITHM,
            )

        except Exception:
            logger.exception(
                "Error creating JWT for user: %s",
                user.id,
            )
            return None

    def decode_jwt(
        self,
        token: str,
    ) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT."""
        if not isinstance(token, str):
            return None

        token = token.strip()

        if not token:
            return None

        secret = self._get_jwt_secret()

        if not secret:
            return None

        try:
            payload = jwt.decode(
                token,
                secret,
                algorithms=[JWT_ALGORITHM],
            )

            if not payload.get("sub"):
                return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.info("JWT has expired")
            return None

        except jwt.InvalidTokenError:
            logger.info("Invalid JWT supplied")
            return None

        except Exception:
            logger.exception("Unexpected JWT validation error")
            return None
    # =============================================================================
# Flask-Login Integration
# =============================================================================

def init_login_manager(app):
    """Initialize Flask-Login with the application."""

    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    return login_manager


# =============================================================================
# Global User Manager
# =============================================================================

_user_manager: Optional[UserManager] = None


def get_user_manager() -> UserManager:
    """Return the application-wide UserManager instance."""
    global _user_manager

    if _user_manager is None:
        _user_manager = UserManager()

    return _user_manager


# =============================================================================
# Flask-Login User Loader
# =============================================================================

@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    """Load a user for Flask-Login."""
    try:
        return get_user_manager().get_user_by_id(user_id)
    except Exception:
        logger.exception(
            "Error loading authenticated user: %s",
            user_id,
        )
        return None


# =============================================================================
# Authentication Helpers
# =============================================================================

def _is_safe_redirect_target(target: Optional[str]) -> bool:
    """
    Validate that a redirect target points to the current application.

    Prevents external/open redirects through the login `next` parameter.
    """
    if not target:
        return False

    try:
        host_url = urlparse(request.host_url)
        target_url = urlparse(
            urljoin(request.host_url, target)
        )

        return (
            target_url.scheme in {"http", "https"}
            and target_url.netloc == host_url.netloc
        )

    except Exception:
        return False


def _get_safe_next_url(
    target: Optional[str],
) -> Optional[str]:
    """Return a safe local redirect target or None."""
    if _is_safe_redirect_target(target):
        return target

    return None


def _get_request_token() -> Optional[str]:
    """Extract a bearer token from the Authorization header."""
    authorization = request.headers.get(
        "Authorization",
        "",
    ).strip()

    if not authorization:
        return None

    parts = authorization.split(None, 1)

    if len(parts) != 2:
        return None

    scheme, token = parts

    if scheme.lower() != "bearer":
        return None

    token = token.strip()

    return token or None


def _json_error(
    message: str,
    status_code: int = 400,
):
    """Return a consistent JSON error response."""
    return jsonify({
        "success": False,
        "error": message,
    }), status_code


# =============================================================================
# API-Key Authentication Decorator
# =============================================================================

def api_key_required(view_func):
    """
    Require a valid UBP API key.

    The authenticated user is made available through `current_user`.
    """

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        api_key = request.headers.get(
            "X-API-Key",
        )

        if not api_key:
            api_key = request.args.get(
                "api_key",
            )

        if not api_key:
            return _json_error(
                "API key required",
                401,
            )

        manager = get_user_manager()

        user = manager.get_user_by_api_key(
            api_key,
        )

        if not user:
            return _json_error(
                "Invalid API key",
                401,
            )

        if not user.is_active:
            return _json_error(
                "Account is inactive",
                403,
            )

        manager.update_api_key_usage(
            api_key,
        )

        # Preserve the authenticated user for the request.
        from flask import g

        g.api_user = user

        return view_func(*args, **kwargs)

    return wrapped


# =============================================================================
# Role Authorization Decorator
# =============================================================================

def role_required(*roles):
    """Require the current user to have one of the supplied roles."""

    allowed_roles = {
        str(role).strip().lower()
        for role in roles
        if role
    }

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(
                    url_for(
                        "auth.login",
                        next=request.url,
                    )
                )

            user_role = (
                getattr(current_user, "role", "user")
                or "user"
            ).lower()

            if user_role not in allowed_roles:
                if request.is_json:
                    return _json_error(
                        "Insufficient permissions",
                        403,
                    )

                flash(
                    "You do not have permission to access this page.",
                    "danger",
                )

                return redirect(
                    url_for("index")
                )

            return view_func(*args, **kwargs)

        return wrapped

    return decorator


# =============================================================================
# Login
# =============================================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate a user."""
    if current_user.is_authenticated:
        return redirect(
            url_for("index")
        )

    if request.method == "GET":
        return render_template(
            "auth/login.html"
        )

    username = (
        request.form.get("username")
        or request.form.get("email")
        or ""
    ).strip()

    password = request.form.get(
        "password",
        "",
    )

    remember = (
        request.form.get("remember")
        in {"1", "true", "True", "on", "yes"}
    )

    if not username or not password:
        flash(
            "Please enter your username and password.",
            "danger",
        )

        return render_template(
            "auth/login.html"
        )

    manager = get_user_manager()

    user = manager.authenticate(
        username,
        password,
    )

    if not user:
        flash(
            "Invalid username or password.",
            "danger",
        )

        return render_template(
            "auth/login.html"
        )

    if not user.is_active:
        flash(
            "Your account is inactive.",
            "danger",
        )

        return render_template(
            "auth/login.html"
        )

    # Validate the optional redirect target.
    next_url = _get_safe_next_url(
        request.args.get("next")
    )

    login_user(
        user,
        remember=remember,
    )

    flash(
        "Login successful.",
        "success",
    )

    return redirect(
        next_url or url_for("index")
    )


# =============================================================================
# Registration
# =============================================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user."""
    if current_user.is_authenticated:
        return redirect(
            url_for("index")
        )

    if request.method == "GET":
        return render_template(
            "auth/register.html"
        )

    username = (
        request.form.get("username")
        or ""
    ).strip()

    email = (
        request.form.get("email")
        or ""
    ).strip().lower()

    password = request.form.get(
        "password",
        "",
    )

    confirm_password = request.form.get(
        "confirm_password",
        "",
    )

    if not username or not email or not password:
        flash(
            "Please fill in all required fields.",
            "danger",
        )

        return render_template(
            "auth/register.html"
        )

    if password != confirm_password:
        flash(
            "Passwords do not match.",
            "danger",
        )

        return render_template(
            "auth/register.html"
        )

    if len(password) < MIN_PASSWORD_LENGTH:
        flash(
            f"Password must be at least "
            f"{MIN_PASSWORD_LENGTH} characters.",
            "danger",
        )

        return render_template(
            "auth/register.html"
        )

    manager = get_user_manager()

    user = manager.create_user(
        username=username,
        email=email,
        password=password,
        role="user",
    )

    if not user:
        flash(
            "Username or email may already be registered.",
            "danger",
        )

        return render_template(
            "auth/register.html"
        )

    flash(
        "Registration successful. You can now log in.",
        "success",
    )

    return redirect(
        url_for("auth.login")
    )


# =============================================================================
# Logout
# =============================================================================

@auth_bp.route("/logout")
@login_required
def logout():
    """Log out the current user."""
    username = getattr(
        current_user,
        "username",
        "unknown",
    )

    logout_user()

    logger.info(
        "User logged out: %s",
        username,
    )

    flash(
        "You have been logged out.",
        "success",
    )

    return redirect(
        url_for("auth.login")
    )


# =============================================================================
# Profile
# =============================================================================

@auth_bp.route("/profile")
@login_required
def profile():
    """Display the current user's profile."""
    manager = get_user_manager()

    user = manager.get_user_by_id(
        current_user.id
    )

    if not user:
        logout_user()

        flash(
            "Your account could not be found.",
            "danger",
        )

        return redirect(
            url_for("auth.login")
        )

    api_keys = manager.list_api_keys(
        user.id
    )

    return render_template(
        "auth/profile.html",
        user=user,
        api_keys=api_keys,
    )


# =============================================================================
# API-Key Routes
# =============================================================================

@auth_bp.route(
    "/api-key/create",
    methods=["POST"],
)
@login_required
def create_api_key():
    """Create an API key for the current user."""
    name = (
        request.form.get("name")
        or request.json.get("name")
        if request.is_json
        else request.form.get("name")
    )

    if not name:
        name = "Default"

    manager = get_user_manager()

    api_key = manager.create_api_key(
        current_user.id,
        name=name,
    )

    if not api_key:
        if request.is_json:
            return _json_error(
                "Unable to create API key",
                500,
            )

        flash(
            "Failed to create API key.",
            "danger",
        )

        return redirect(
            url_for("auth.profile")
        )

    if request.is_json:
        return jsonify({
            "success": True,
            "api_key": api_key,
            "message": (
                "Store this API key securely. "
                "It will not be shown again."
            ),
        })

    flash(
        "API key created successfully. "
        "Store it securely because it will not be shown again.",
        "success",
    )

    return redirect(
        url_for("auth.profile")
    )


@auth_bp.route(
    "/api-key/revoke/<int:key_id>",
    methods=["POST"],
)
@login_required
def revoke_api_key(key_id: int):
    """Revoke one of the current user's API keys."""
    manager = get_user_manager()

    success = manager.revoke_api_key(
        key_id=key_id,
        user_id=current_user.id,
    )

    if not success:
        if request.is_json:
            return _json_error(
                "API key not found or already revoked",
                404,
            )

        flash(
            "API key could not be revoked.",
            "danger",
        )

        return redirect(
            url_for("auth.profile")
        )

    if request.is_json:
        return jsonify({
            "success": True,
            "message": "API key revoked successfully.",
        })

    flash(
        "API key revoked successfully.",
        "success",
    )

    return redirect(
        url_for("auth.profile")
    )


# =============================================================================
# Two-Factor Authentication
# =============================================================================

@auth_bp.route(
    "/setup-2fa",
    methods=["GET"],
)
@login_required
def setup_2fa():
    """Set up TOTP-based two-factor authentication."""
    manager = get_user_manager()

    secret = manager.setup_2fa(
        current_user.id
    )

    if not secret:
        flash(
            "Unable to set up two-factor authentication.",
            "danger",
        )

        return redirect(
            url_for("auth.profile")
        )

    issuer = (
        current_app.config.get(
            "TOTP_ISSUER",
            "UBP Blockchain Toolkit",
        )
    )

    provisioning_uri = pyotp.TOTP(
        secret
    ).provisioning_uri(
        name=current_user.email,
        issuer_name=issuer,
    )

    qr_image = qrcode.make(
        provisioning_uri
    )

    buffer = BytesIO()
    qr_image.save(
        buffer,
        format="PNG",
    )

    qr_code = (
        "data:image/png;base64,"
        + __import__("base64").b64encode(
            buffer.getvalue()
        ).decode("utf-8")
    )

    return render_template(
        "auth/setup_2fa.html",
        secret=secret,
        provisioning_uri=provisioning_uri,
        qr_code=qr_code,
    )


@auth_bp.route(
    "/verify-2fa",
    methods=["POST"],
)
@login_required
def verify_2fa():
    """Verify and enable 2FA."""
    code = (
        request.form.get("code")
        or ""
    ).strip()

    if not code:
        flash(
            "Please enter your 2FA code.",
            "danger",
        )

        return redirect(
            url_for("auth.setup_2fa")
        )

    manager = get_user_manager()

    if manager.verify_2fa(
        current_user.id,
        code,
    ):
        flash(
            "2FA enabled successfully!",
            "success",
        )
    else:
        flash(
            "Invalid 2FA code. Please try again.",
            "danger",
        )

    return redirect(
        url_for("auth.profile")
    )


@auth_bp.route(
    "/disable-2fa",
    methods=["POST"],
)
@login_required
def disable_2fa():
    """Disable 2FA."""
    manager = get_user_manager()

    if manager.disable_2fa(
        current_user.id
    ):
        flash(
            "2FA disabled successfully.",
            "success",
        )
    else:
        flash(
            "Failed to disable 2FA.",
            "danger",
        )

    return redirect(
        url_for("auth.profile")
    )


# =============================================================================
# Change Password
# =============================================================================

@auth_bp.route(
    "/change-password",
    methods=["POST"],
)
@login_required
def change_password():
    """Change the current user's password."""
    current_password = request.form.get(
        "current_password",
        "",
    )

    new_password = request.form.get(
        "new_password",
        "",
    )

    confirm_password = request.form.get(
        "confirm_password",
        "",
    )

    if not current_password or not new_password:
        flash(
            "Please fill in all fields.",
            "danger",
        )

        return redirect(
            url_for("auth.profile")
        )

    if new_password != confirm_password:
        flash(
            "Passwords do not match.",
            "danger",
        )

        return redirect(
            url_for("auth.profile")
        )

    if len(new_password) < MIN_PASSWORD_LENGTH:
        flash(
            f"Password must be at least "
            f"{MIN_PASSWORD_LENGTH} characters.",
            "danger",
        )

        return redirect(
            url_for("auth.profile")
        )

    manager = get_user_manager()

    user = manager.get_user_by_id(
        current_user.id
    )

    if not user:
        flash(
            "User account could not be found.",
            "danger",
        )

        return redirect(
            url_for("auth.profile")
        )

    # Verify the existing password using the database record.
    conn = manager._get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT password_hash
            FROM users
            WHERE id = ?
              AND is_active = 1
            LIMIT 1
            """,
            (str(current_user.id),),
        )

        row = cursor.fetchone()

    except Exception:
        logger.exception(
            "Error retrieving password hash for user: %s",
            current_user.id,
        )

        flash(
            "Unable to change password. Please try again.",
            "danger",
        )

        return redirect(
            url_for("auth.profile")
        )

    finally:
        conn.close()

    if not row:
        flash(
            "User account could not be found.",
            "danger",
        )

        return redirect(
            url_for("auth.profile")
        )

    try:
        password_valid = bcrypt.check_password_hash(
            row["password_hash"],
            current_password,
        )
    except (ValueError, TypeError):
        password_valid = False

    if not password_valid:
        flash(
            "Current password is incorrect.",
            "danger",
        )

        return redirect(
            url_for("auth.profile")
        )

    if not manager.update_password(
        current_user.id,
        new_password,
    ):
        flash(
            "Failed to change password.",
            "danger",
        )

        return redirect(
            url_for("auth.profile")
        )

    flash(
        "Password changed successfully!",
        "success",
    )

    return redirect(
        url_for("auth.profile")
    )


# =============================================================================
# Password Reset
# =============================================================================

@auth_bp.route(
    "/forgot-password",
    methods=["GET", "POST"],
)
def forgot_password():
    """Request a password reset."""
    if request.method == "GET":
        return render_template(
            "auth/forgot_password.html"
        )

    email = (
        request.form.get("email")
        or ""
    ).strip().lower()

    if not email:
        flash(
            "Please enter your email address.",
            "danger",
        )

        return render_template(
            "auth/forgot_password.html"
        )

    manager = get_user_manager()

    user = manager.get_user_by_email(
        email
    )

    # Do not disclose whether an email exists.
    if user:
        token = manager.create_password_reset_token(
            user.id
        )

        if token:
            # The existing application can replace this with its email
            # delivery implementation. We intentionally don't expose the
            # token in the HTTP response.
            logger.info(
                "Password reset requested for user: %s",
                user.id,
            )

            # If an email service is configured, use it.
            mailer = current_app.extensions.get(
                "mailer"
            )

            if mailer:
                try:
                    reset_url = url_for(
                        "auth.reset_password",
                        token=token,
                        _external=True,
                    )

                    mailer.send_password_reset(
                        email,
                        reset_url,
                    )

                except Exception:
                    logger.exception(
                        "Failed to send password reset email"
                    )

    flash(
        "If an account exists for that email, "
        "password-reset instructions have been sent.",
        "info",
    )

    return redirect(
        url_for("auth.login")
    )


@auth_bp.route(
    "/reset-password/<token>",
    methods=["GET", "POST"],
)
def reset_password(token: str):
    """Reset a password using a valid reset token."""
    if not token:
        flash(
            "Invalid password reset link.",
            "danger",
        )

        return redirect(
            url_for("auth.login")
        )

    manager = get_user_manager()

    user_id = manager.verify_password_reset_token(
        token
    )

    if not user_id:
        flash(
            "This password reset link is invalid or has expired.",
            "danger",
        )

        return redirect(
            url_for("auth.login")
        )

    if request.method == "GET":
        return render_template(
            "auth/reset_password.html",
            token=token,
        )

    new_password = request.form.get(
        "password",
        "",
    )

    confirm_password = request.form.get(
        "confirm_password",
        "",
    )

    if not new_password:
        flash(
            "Please enter a new password.",
            "danger",
        )

        return render_template(
            "auth/reset_password.html",
            token=token,
        )

    if new_password != confirm_password:
        flash(
            "Passwords do not match.",
            "danger",
        )

        return render_template(
            "auth/reset_password.html",
            token=token,
        )

    if len(new_password) < MIN_PASSWORD_LENGTH:
        flash(
            f"Password must be at least "
            f"{MIN_PASSWORD_LENGTH} characters.",
            "danger",
        )

        return render_template(
            "auth/reset_password.html",
            token=token,
        )

    # Consume the token only immediately before the password update.
    consumed_user_id = manager.consume_password_reset_token(
        token
    )

    if not consumed_user_id:
        flash(
            "This password reset link is invalid or has expired.",
            "danger",
        )

        return redirect(
            url_for("auth.login")
        )

    if not manager.update_password(
        consumed_user_id,
        new_password,
    ):
        flash(
            "Unable to reset your password. Please try again.",
            "danger",
        )

        return redirect(
            url_for("auth.login")
        )

    flash(
        "Password reset successfully. You can now log in.",
        "success",
    )

    return redirect(
        url_for("auth.login")
    )


# =============================================================================
# JWT Authentication
# =============================================================================

def jwt_required(view_func):
    """Require a valid JWT bearer token."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        token = _get_request_token()

        if not token:
            return _json_error(
                "Bearer token required",
                401,
            )

        manager = get_user_manager()

        payload = manager.decode_jwt(
            token
        )

        if not payload:
            return _json_error(
                "Invalid or expired token",
                401,
            )

        user = manager.get_user_by_id(
            payload.get("sub")
        )

        if not user:
            return _json_error(
                "User not found",
                401,
            )

        if not user.is_active:
            return _json_error(
                "Account is inactive",
                403,
            )

        from flask import g

        g.jwt_user = user

        return view_func(
            *args,
            **kwargs,
        )

    return wrapped


# =============================================================================
# Blueprint Registration Helper
# =============================================================================

def init_auth(app):
    """
    Initialize authentication for a Flask application.

    This preserves the existing blueprint-based architecture.
    """
    init_login_manager(app)

    if auth_bp.name not in app.blueprints:
        app.register_blueprint(auth_bp)

    return auth_bp


# =============================================================================
# End of File
# =============================================================================