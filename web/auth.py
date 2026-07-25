"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
web.auth

Purpose
-------
User authentication for the web interface.

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

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import jwt
import hashlib
import secrets
import sqlite3
import json

from core.logger import get_logger

logger = get_logger(__name__)

# Setup auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Setup bcrypt
bcrypt = Bcrypt()

# JWT secret
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_hex(32))
JWT_EXPIRY = int(os.getenv("JWT_EXPIRY", "3600"))


class User(UserMixin):
    """
    User model for authentication.
    """
    
    def __init__(self, id, username, email, password_hash, role='user', created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at or datetime.utcnow()


class UserManager:
    """
    User management for authentication.
    """
    
    def __init__(self, db_path="ubp.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the users table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    api_key TEXT UNIQUE
                )
            """)
            
            # Create API keys table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    api_key TEXT UNIQUE NOT NULL,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("User database initialized")
        except Exception as e:
            logger.error(f"Error initializing user database: {e}")
    
    def create_user(self, username, email, password, role='user'):
        """Create a new user."""
        try:
            user_id = secrets.token_urlsafe(16)
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            api_key = f"ubp_{secrets.token_hex(24)}"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (id, username, email, password_hash, role, api_key)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, username, email, password_hash, role, api_key))
            
            conn.commit()
            conn.close()
            
            logger.info(f"User created: {username}")
            return User(user_id, username, email, password_hash, role)
        except sqlite3.IntegrityError as e:
            logger.error(f"User creation failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User(row[0], row[1], row[2], row[3], row[4], row[5])
            return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def get_user_by_username(self, username):
        """Get user by username."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User(row[0], row[1], row[2], row[3], row[4], row[5])
            return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def get_user_by_api_key(self, api_key):
        """Get user by API key."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE api_key = ? AND is_active = 1", (api_key,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User(row[0], row[1], row[2], row[3], row[4], row[5])
            return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def authenticate(self, username, password):
        """Authenticate a user."""
        user = self.get_user_by_username(username)
        if not user:
            return None
        
        if bcrypt.check_password_hash(user.password_hash, password):
            # Update last login
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user.id,))
                conn.commit()
                conn.close()
            except:
                pass
            return user
        
        return None
    
    def create_api_key(self, user_id, name):
        """Create an API key for a user."""
        try:
            api_key_id = secrets.token_urlsafe(12)
            api_key = f"ubp_{secrets.token_hex(32)}"
            expires_at = datetime.utcnow() + timedelta(days=90)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO api_keys (id, user_id, api_key, name, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (api_key_id, user_id, api_key, name, expires_at))
            
            conn.commit()
            conn.close()
            
            logger.info(f"API key created for user {user_id}")
            return api_key
        except Exception as e:
            logger.error(f"Error creating API key: {e}")
            return None
    
    def get_api_keys(self, user_id):
        """Get all API keys for a user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, api_key, name, created_at, last_used, expires_at, is_active
                FROM api_keys WHERE user_id = ?
            """, (user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                "id": row[0],
                "api_key": row[1][:10] + "...",
                "name": row[2],
                "created_at": row[3],
                "last_used": row[4],
                "expires_at": row[5],
                "is_active": row[6],
            } for row in rows]
        except Exception as e:
            logger.error(f"Error getting API keys: {e}")
            return []
    
    def revoke_api_key(self, api_key_id, user_id):
        """Revoke an API key."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE api_keys SET is_active = 0
                WHERE id = ? AND user_id = ?
            """, (api_key_id, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error revoking API key: {e}")
            return False


# Global user manager
_user_manager = None

def get_user_manager():
    """Get the user manager instance."""
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager()
    return _user_manager


# ============ Flask-Login User Loader ============

def load_user(user_id):
    """Load user for Flask-Login."""
    return get_user_manager().get_user_by_id(user_id)


# ============ Auth Routes ============

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = get_user_manager().authenticate(username, password)
        if user:
            login_user(user)
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(request.args.get('next') or url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register page."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters', 'danger')
            return render_template('register.html')
        
        user = get_user_manager().create_user(username, email, password)
        if user:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Username or email already exists', 'danger')
    
    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page."""
    user_manager = get_user_manager()
    api_keys = user_manager.get_api_keys(current_user.id)
    return render_template('profile.html', user=current_user, api_keys=api_keys)


@auth_bp.route('/api-key/create', methods=['POST'])
@login_required
def create_api_key():
    """Create a new API key."""
    name = request.form.get('name', 'Default')
    user_manager = get_user_manager()
    api_key = user_manager.create_api_key(current_user.id, name)
    
    if api_key:
        flash(f'API Key created: {api_key}', 'success')
        return redirect(url_for('auth.profile'))
    else:
        flash('Failed to create API key', 'danger')
        return redirect(url_for('auth.profile'))


@auth_bp.route('/api-key/revoke/<key_id>', methods=['POST'])
@login_required
def revoke_api_key(key_id):
    """Revoke an API key."""
    user_manager = get_user_manager()
    if user_manager.revoke_api_key(key_id, current_user.id):
        flash('API key revoked', 'success')
    else:
        flash('Failed to revoke API key', 'danger')
    return redirect(url_for('auth.profile'))


# ============ API Key Authentication ============

def authenticate_api_key(request):
    """Authenticate an API key from the request."""
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return None
    
    user_manager = get_user_manager()
    user = user_manager.get_user_by_api_key(api_key)
    
    if user:
        # Update last used
        try:
            conn = sqlite3.connect(user_manager.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE api_keys SET last_used = CURRENT_TIMESTAMP
                WHERE api_key = ? AND is_active = 1
            """, (api_key,))
            conn.commit()
            conn.close()
        except:
            pass
    
    return user


def require_api_key(func):
    """Decorator to require API key authentication."""
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = authenticate_api_key(request)
        if user:
            # Add user to request context
            request.user = user
            return func(*args, **kwargs)
        return jsonify({"error": "Invalid or missing API key"}), 401
    return wrapper


# ============ JWT Token Generation ============

def generate_jwt_token(user_id, role='user'):
    """Generate a JWT token for a user."""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXPIRY)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def verify_jwt_token(token):
    """Verify a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


###############################################################################
# End of File
###############################################################################
