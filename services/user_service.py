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

import uuid
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash

from database.database import get_db_manager
from database.models import User, Wallet, UserTransaction
from core.logger import get_logger

logger = get_logger(__name__)


class UserService:
    """User account management service."""

    def __init__(self):
        self.db = get_db_manager()

    def create_user(self, username: str, email: str, password: str, role: str = "user") -> Optional[User]:
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
        try:
            with self.db.get_session() as session:
                existing = session.query(User).filter(
                    (User.username == username) | (User.email == email)
                ).first()

                if existing:
                    logger.warning(f"User already exists: {username}")
                    return None

                # Generate API key
                api_key = f"ubp_{secrets.token_hex(24)}"

                # Create user
                user = User(
                    username=username,
                    email=email,
                    password_hash=generate_password_hash(password),
                    role=role,
                    api_key=api_key,
                    created_at=datetime.utcnow(),
                    is_active=True,
                )

                session.add(user)
                session.flush()
                
                # Refresh to load all attributes
                session.refresh(user)
                
                # Detach the user from the session so it can be used outside
                session.expunge(user)

                logger.info(f"User created: {username} ({email})")
                return user

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    def authenticate(self, username: str, password: str) -> Optional[User]:
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
        try:
            with self.db.get_session() as session:
                user = session.query(User).filter(
                    User.username == username
                ).first()

                if not user:
                    logger.warning(f"User not found: {username}")
                    return None

                if not user.is_active:
                    logger.warning(f"Inactive user attempted login: {username}")
                    return None

                if check_password_hash(user.password_hash, password):
                    # Update last login
                    user.last_login = datetime.utcnow()
                    session.flush()
                    
                    # Detach the user from the session so it can be used outside
                    session.expunge(user)
                    
                    logger.info(f"User authenticated: {username}")
                    return user

                logger.warning(f"Invalid password for user: {username}")
                return None

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            user_uuid = uuid.UUID(str(user_id))

            with self.db.get_session() as session:
                user = (
                    session.query(User)
                    .filter(User.id == user_uuid)
                    .first()
                )

                if user:
                    session.expunge(user)

                return user

        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Invalid user ID: {user_id} - {e}")
            return None

        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        try:
            with self.db.get_session() as session:
                user = session.query(User).filter(User.username == username).first()
                if user:
                    session.expunge(user)
                return user
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            with self.db.get_session() as session:
                user = session.query(User).filter(User.email == email).first()
                if user:
                    session.expunge(user)
                return user
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """Get user by API key."""
        try:
            with self.db.get_session() as session:
                user = session.query(User).filter(
                    User.api_key == api_key,
                    User.is_active == True
                ).first()
                
                if user:
                    session.expunge(user)
                
                return user
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    def update_user(self, user_id: str, **kwargs) -> bool:
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
        try:
            with self.db.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    logger.warning(f"User not found: {user_id}")
                    return False

                for key, value in kwargs.items():
                    if hasattr(user, key):
                        # Skip password hash updates (use change_password instead)
                        if key == "password_hash":
                            continue
                        setattr(user, key, value)

                user.updated_at = datetime.utcnow()
                session.flush()
                logger.info(f"User updated: {user_id}")
                return True

        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False

    def change_password(self, user_id: str, new_password: str) -> bool:
        """
        Change user password.

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
        try:
            with self.db.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    logger.warning(f"User not found: {user_id}")
                    return False

                user.password_hash = generate_password_hash(new_password)
                user.updated_at = datetime.utcnow()
                session.flush()
                logger.info(f"Password changed for user: {user_id}")
                return True

        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False

    def regenerate_api_key(self, user_id: str) -> Optional[str]:
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
        try:
            with self.db.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    logger.warning(f"User not found: {user_id}")
                    return None

                new_api_key = f"ubp_{secrets.token_hex(24)}"
                user.api_key = new_api_key
                user.updated_at = datetime.utcnow()
                session.flush()
                logger.info(f"API key regenerated for user: {user_id}")
                return new_api_key

        except Exception as e:
            logger.error(f"Error regenerating API key: {e}")
            return None

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user account (soft delete).

        Parameters
        ----------
        user_id : str
            User ID.

        Returns
        -------
        bool
            True if deleted, False otherwise.
        """
        try:
            with self.db.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    logger.warning(f"User not found: {user_id}")
                    return False

                user.is_active = False
                user.updated_at = datetime.utcnow()
                session.flush()
                logger.info(f"User deactivated: {user_id}")
                return True

        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False

    def list_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all users (admin only).

        Parameters
        ----------
        limit : int
            Maximum number of users to return.
        offset : int
            Offset for pagination.

        Returns
        -------
        List[Dict[str, Any]]
            List of user dictionaries.
        """
        try:
            with self.db.get_session() as session:
                users = session.query(User).order_by(
                    User.created_at.desc()
                ).limit(limit).offset(offset).all()
                
                result = []
                for user in users:
                    session.expunge(user)
                    result.append(self.user_to_dict(user))
                
                return result
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []

    def get_user_count(self) -> int:
        """Get total number of users."""
        try:
            with self.db.get_session() as session:
                return session.query(User).count()
        except Exception as e:
            logger.error(f"Error counting users: {e}")
            return 0

    def user_to_dict(self, user: User) -> Dict[str, Any]:
        """
        Convert User object to dictionary.

        Parameters
        ----------
        user : User
            User object.

        Returns
        -------
        Dict[str, Any]
            User dictionary (without sensitive data).
        """
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "two_factor_enabled": user.two_factor_enabled,
            "default_network": user.default_network,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "api_key": user.api_key,
        }

    def info(self) -> Dict[str, Any]:
        """Return service information."""
        return {
            "service": "User Service",
            "version": "2.0 Enterprise",
            "total_users": self.get_user_count(),
        }


###############################################################################
# End of File
###############################################################################
