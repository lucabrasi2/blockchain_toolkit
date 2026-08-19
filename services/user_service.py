"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.user_service

Purpose
-------
User account management service.

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

import secrets
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from database.database import get_db_manager
from database.models import User, UserTransaction, Wallet
from core.logger import get_logger


logger = get_logger(__name__)


class UserService:
    """User account management service."""

    # Roles currently supported by the UBP user model.
    VALID_ROLES = {"user", "admin", "viewer", "api"}

    # API keys are generated with a fixed prefix and 24 random bytes.
    API_KEY_PREFIX = "ubp_"
    API_KEY_BYTES = 24

    def __init__(self):
        self.db = get_db_manager()

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    @staticmethod
    def _normalize_username(username: str) -> Optional[str]:
        """Normalize and validate a username."""
        if not isinstance(username, str):
            return None

        username = username.strip()

        if not username:
            return None

        return username

    @staticmethod
    def _normalize_email(email: str) -> Optional[str]:
        """Normalize and validate an email address."""
        if not isinstance(email, str):
            return None

        email = email.strip().lower()

        if not email:
            return None

        return email

    @staticmethod
    def _normalize_password(password: str) -> Optional[str]:
        """Validate a password value without imposing a new policy."""
        if not isinstance(password, str):
            return None

        if not password:
            return None

        return password

    @classmethod
    def _normalize_role(cls, role: str) -> Optional[str]:
        """Normalize and validate a user role."""
        if not isinstance(role, str):
            return None

        role = role.strip().lower()

        if role not in cls.VALID_ROLES:
            return None

        return role

    @staticmethod
    def _parse_user_id(user_id: str) -> Optional[uuid.UUID]:
        """Convert a user ID into a UUID safely."""
        if user_id is None:
            return None

        try:
            return uuid.UUID(str(user_id))
        except (ValueError, TypeError, AttributeError):
            return None

    @classmethod
    def _generate_api_key(cls) -> str:
        """Generate a cryptographically secure UBP API key."""
        return (
            f"{cls.API_KEY_PREFIX}"
            f"{secrets.token_hex(cls.API_KEY_BYTES)}"
        )

    # =========================================================================
    # User Creation & Authentication
    # =========================================================================

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "user",
    ) -> Optional[User]:
        """
        Create a new user account.

        Parameters
        ----------
        username : str
            Unique username.
        email : str
            Unique email address.
        password : str
            User password (will be hashed).
        role : str
            User role (user, admin, viewer, api).

        Returns
        -------
        Optional[User]
            Created user object or None if failed.
        """
        normalized_username = self._normalize_username(username)
        normalized_email = self._normalize_email(email)
        normalized_password = self._normalize_password(password)
        normalized_role = self._normalize_role(role)

        if not normalized_username:
            logger.warning("User creation rejected: empty username")
            return None

        if not normalized_email:
            logger.warning("User creation rejected: empty email")
            return None

        if not normalized_password:
            logger.warning("User creation rejected: empty password")
            return None

        if not normalized_role:
            logger.warning(
                "User creation rejected: invalid role for username=%s",
                normalized_username,
            )
            return None

        try:
            with self.db.get_session() as session:
                existing = session.query(User).filter(
                    (User.username == normalized_username)
                    | (User.email == normalized_email)
                ).first()

                if existing:
                    logger.warning(
                        "User already exists: %s",
                        normalized_username,
                    )
                    return None

                user = User(
                    username=normalized_username,
                    email=normalized_email,
                    password_hash=generate_password_hash(
                        normalized_password
                    ),
                    role=normalized_role,
                    api_key=self._generate_api_key(),
                    created_at=datetime.utcnow(),
                    is_active=True,
                )

                session.add(user)
                session.flush()

                # Refresh to load generated/default database attributes.
                session.refresh(user)

                # Detach the user so callers can safely use it after the
                # database session closes.
                session.expunge(user)

                logger.info(
                    "User created: %s (%s)",
                    normalized_username,
                    normalized_email,
                )

                return user

        except Exception as exc:
            logger.error(
                "Error creating user: %s",
                exc,
            )
            return None

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> Optional[User]:
        """
        Authenticate a user.

        Parameters
        ----------
        username : str
            Username.
        password : str
            Password.

        Returns
        -------
        Optional[User]
            User object if authenticated, None otherwise.
        """
        normalized_username = self._normalize_username(username)

        if not normalized_username or not isinstance(password, str):
            logger.warning("Authentication rejected: invalid credentials")
            return None

        try:
            with self.db.get_session() as session:
                user = (
                    session.query(User)
                    .filter(User.username == normalized_username)
                    .first()
                )

                if not user:
                    logger.warning(
                        "User not found: %s",
                        normalized_username,
                    )
                    return None

                if not user.is_active:
                    logger.warning(
                        "Inactive user attempted login: %s",
                        normalized_username,
                    )
                    return None

                if not check_password_hash(
                    user.password_hash,
                    password,
                ):
                    logger.warning(
                        "Invalid password for user: %s",
                        normalized_username,
                    )
                    return None

                # Update last login only after successful authentication.
                user.last_login = datetime.utcnow()
                session.flush()

                # Detach the user so it can safely be returned after the
                # session closes.
                session.expunge(user)

                logger.info(
                    "User authenticated: %s",
                    normalized_username,
                )

                return user

        except Exception as exc:
            logger.error(
                "Authentication error: %s",
                exc,
            )
            return None

    # =========================================================================
    # User Lookup
    # =========================================================================

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        user_uuid = self._parse_user_id(user_id)

        if not user_uuid:
            logger.error(
                "Invalid user ID: %s",
                user_id,
            )
            return None

        try:
            with self.db.get_session() as session:
                user = (
                    session.query(User)
                    .filter(User.id == user_uuid)
                    .first()
                )

                if user:
                    session.expunge(user)

                return user

        except Exception as exc:
            logger.error(
                "Error getting user: %s",
                exc,
            )
            return None

    def get_user_by_username(
        self,
        username: str,
    ) -> Optional[User]:
        """Get user by username."""
        normalized_username = self._normalize_username(username)

        if not normalized_username:
            return None

        try:
            with self.db.get_session() as session:
                user = (
                    session.query(User)
                    .filter(User.username == normalized_username)
                    .first()
                )

                if user:
                    session.expunge(user)

                return user

        except Exception as exc:
            logger.error(
                "Error getting user by username: %s",
                exc,
            )
            return None

    def get_user_by_email(
        self,
        email: str,
    ) -> Optional[User]:
        """Get user by email."""
        normalized_email = self._normalize_email(email)

        if not normalized_email:
            return None

        try:
            with self.db.get_session() as session:
                user = (
                    session.query(User)
                    .filter(User.email == normalized_email)
                    .first()
                )

                if user:
                    session.expunge(user)

                return user

        except Exception as exc:
            logger.error(
                "Error getting user by email: %s",
                exc,
            )
            return None
        # =========================================================================
    # API-Key Lookup
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

        try:
            with self.db.get_session() as session:
                user = (
                    session.query(User)
                    .filter(
                        User.api_key == api_key,
                        User.is_active.is_(True),
                    )
                    .first()
                )

                if user:
                    session.expunge(user)

                return user

        except Exception as exc:
            logger.error(
                "Error getting user by API key: %s",
                exc,
            )
            return None

    # =========================================================================
    # User Updates
    # =========================================================================

    def update_user(
        self,
        user_id: str,
        **kwargs: Any,
    ) -> bool:
        """
        Update user information.

        Parameters
        ----------
        user_id : str
            User ID.
        **kwargs
            Fields to update.

        Returns
        -------
        bool
            True if updated, False otherwise.
        """
        user_uuid = self._parse_user_id(user_id)

        if not user_uuid:
            logger.warning(
                "User update rejected: invalid user ID: %s",
                user_id,
            )
            return False

        if not kwargs:
            logger.warning(
                "User update rejected: no fields supplied for %s",
                user_id,
            )
            return False

        try:
            with self.db.get_session() as session:
                user = (
                    session.query(User)
                    .filter(User.id == user_uuid)
                    .first()
                )

                if not user:
                    logger.warning(
                        "User not found: %s",
                        user_id,
                    )
                    return False

                # Fields that must never be changed through the generic
                # update method.
                protected_fields = {
                    "id",
                    "password_hash",
                    "api_key",
                    "created_at",
                }

                for key, value in kwargs.items():
                    if key in protected_fields:
                        continue

                    if not hasattr(user, key):
                        logger.warning(
                            "Ignoring unknown user field: %s",
                            key,
                        )
                        continue

                    # Normalize supported user-facing fields.
                    if key == "username":
                        value = self._normalize_username(value)
                        if not value:
                            logger.warning(
                                "Invalid username supplied for %s",
                                user_id,
                            )
                            return False

                    elif key == "email":
                        value = self._normalize_email(value)
                        if not value:
                            logger.warning(
                                "Invalid email supplied for %s",
                                user_id,
                            )
                            return False

                    elif key == "role":
                        value = self._normalize_role(value)
                        if not value:
                            logger.warning(
                                "Invalid role supplied for %s",
                                user_id,
                            )
                            return False

                    setattr(user, key, value)

                user.updated_at = datetime.utcnow()
                session.flush()

                logger.info(
                    "User updated: %s",
                    user_id,
                )

                return True

        except Exception as exc:
            logger.error(
                "Error updating user: %s",
                exc,
            )
            return False

    def change_password(
        self,
        user_id: str,
        new_password: str,
    ) -> bool:
        """
        Change user password.

        This method intentionally preserves the existing service contract.
        Password verification for the normal web change-password flow is
        handled by the web authentication layer.

        Parameters
        ----------
        user_id : str
            User ID.
        new_password : str
            New password.

        Returns
        -------
        bool
            True if updated, False otherwise.
        """
        user_uuid = self._parse_user_id(user_id)
        normalized_password = self._normalize_password(new_password)

        if not user_uuid:
            logger.warning(
                "Password change rejected: invalid user ID: %s",
                user_id,
            )
            return False

        if not normalized_password:
            logger.warning(
                "Password change rejected: empty password for %s",
                user_id,
            )
            return False

        try:
            with self.db.get_session() as session:
                user = (
                    session.query(User)
                    .filter(User.id == user_uuid)
                    .first()
                )

                if not user:
                    logger.warning(
                        "User not found: %s",
                        user_id,
                    )
                    return False

                user.password_hash = generate_password_hash(
                    normalized_password
                )
                user.updated_at = datetime.utcnow()

                session.flush()

                logger.info(
                    "Password changed for user: %s",
                    user_id,
                )

                return True

        except Exception as exc:
            logger.error(
                "Error changing password: %s",
                exc,
            )
            return False

    # =========================================================================
    # API-Key Management
    # =========================================================================

    def regenerate_api_key(
        self,
        user_id: str,
    ) -> Optional[str]:
        """
        Regenerate API key for a user.

        Parameters
        ----------
        user_id : str
            User ID.

        Returns
        -------
        Optional[str]
            New API key or None if failed.
        """
        user_uuid = self._parse_user_id(user_id)

        if not user_uuid:
            logger.warning(
                "API key regeneration rejected: invalid user ID: %s",
                user_id,
            )
            return None

        try:
            with self.db.get_session() as session:
                user = (
                    session.query(User)
                    .filter(User.id == user_uuid)
                    .first()
                )

                if not user:
                    logger.warning(
                        "User not found: %s",
                        user_id,
                    )
                    return None

                new_api_key = self._generate_api_key()

                user.api_key = new_api_key
                user.updated_at = datetime.utcnow()

                session.flush()

                logger.info(
                    "API key regenerated for user: %s",
                    user_id,
                )

                return new_api_key

        except Exception as exc:
            logger.error(
                "Error regenerating API key: %s",
                exc,
            )
            return None

    # =========================================================================
    # User Deactivation
    # =========================================================================

    def delete_user(
        self,
        user_id: str,
    ) -> bool:
        """
        Deactivate a user account (soft delete).

        Parameters
        ----------
        user_id : str
            User ID.

        Returns
        -------
        bool
            True if deactivated, False otherwise.
        """
        user_uuid = self._parse_user_id(user_id)

        if not user_uuid:
            logger.warning(
                "User deletion rejected: invalid user ID: %s",
                user_id,
            )
            return False

        try:
            with self.db.get_session() as session:
                user = (
                    session.query(User)
                    .filter(User.id == user_uuid)
                    .first()
                )

                if not user:
                    logger.warning(
                        "User not found: %s",
                        user_id,
                    )
                    return False

                user.is_active = False
                user.updated_at = datetime.utcnow()

                session.flush()

                logger.info(
                    "User deactivated: %s",
                    user_id,
                )

                return True

        except Exception as exc:
            logger.error(
                "Error deleting user: %s",
                exc,
            )
            return False
        # =========================================================================
    # User Listing & Statistics
    # =========================================================================

    def list_users(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List users with pagination.

        Authorization is intentionally handled by the API/web layer.

        Parameters
        ----------
        limit : int
            Maximum number of users to return.
        offset : int
            Number of users to skip.

        Returns
        -------
        List[Dict[str, Any]]
            List of sanitized user dictionaries.
        """
        try:
            # Keep pagination values safe and predictable.
            limit = max(1, min(int(limit), 1000))
            offset = max(0, int(offset))

            with self.db.get_session() as session:
                users = (
                    session.query(User)
                    .order_by(User.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                    .all()
                )

                result: List[Dict[str, Any]] = []

                for user in users:
                    session.expunge(user)
                    result.append(self.user_to_dict(user))

                return result

        except (TypeError, ValueError) as exc:
            logger.error(
                "Invalid pagination values: %s",
                exc,
            )
            return []

        except Exception as exc:
            logger.error(
                "Error listing users: %s",
                exc,
            )
            return []

    def get_user_count(self) -> int:
        """Get total number of users."""
        try:
            with self.db.get_session() as session:
                return session.query(User).count()

        except Exception as exc:
            logger.error(
                "Error counting users: %s",
                exc,
            )
            return 0

    # =========================================================================
    # Serialization
    # =========================================================================

    def user_to_dict(
        self,
        user: User,
    ) -> Dict[str, Any]:
        """
        Convert a User object to a sanitized dictionary.

        Sensitive credentials such as the API key and password hash are
        intentionally excluded.

        Parameters
        ----------
        user : User
            User object.

        Returns
        -------
        Dict[str, Any]
            Sanitized user dictionary.
        """
        if user is None:
            return {}

        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "two_factor_enabled": user.two_factor_enabled,
            "default_network": user.default_network,
            "created_at": (
                user.created_at.isoformat()
                if user.created_at
                else None
            ),
            "last_login": (
                user.last_login.isoformat()
                if user.last_login
                else None
            ),
        }

    # =========================================================================
    # Service Information
    # =========================================================================

    def info(self) -> Dict[str, Any]:
        """Return service information."""
        return {
            "service": "User Service",
            "version": "2.0 Enterprise",
            "total_users": self.get_user_count(),
        }


# =============================================================================
# End of File
# =============================================================================