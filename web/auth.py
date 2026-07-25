"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
web.auth

Purpose
-------
User authentication for the web interface.

This module handles:
    • User registration and login
    • Session management
    • Password hashing and verification
    • Two-Factor Authentication (2FA)
    • API key generation and management
    • User roles and permissions
    • Email notifications

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
import secrets
import hashlib
from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

try:
    import pyotp
    import qrcode
    import io
    import base64
    HAS_2FA = True
except ImportError:
    HAS_2FA = False

from core.logger import get_logger
from web.mailer import send_welcome_email, send_alert_email

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

    def __init__(self, id, username, email, password_hash, role='user', created_at=None, otp_secret=None, otp_enabled=0):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at or datetime.utcnow()
        self.otp_secret = otp_secret
        self.otp_enabled = bool(otp_enabled)
        self._is_active = True

    @property
    def is_active(self):
        return self._is_active


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
                    api_key TEXT UNIQUE,
                    otp_secret TEXT,
                    otp_enabled BOOLEAN DEFAULT 0
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

            # Create email_notifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_notifications (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    subject TEXT,
                    body TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
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

            # Send welcome email
            try:
                send_welcome_email(email, username)
            except Exception as e:
                logger.warning(f"Could not send welcome email: {e}")

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
                return User(row[0], row[1], row[2], row[3], row[4], row[5], row[7], row[8])
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
                return User(row[0], row[1], row[2], row[3], row[4], row[5], row[7], row[8])
            return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    def get_user_by_email(self, email):
        """Get user by email."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return User(row[0], row[1], row[2], row[3], row[4], row[5], row[7], row[8])
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
                return User(row[0], row[1], row[2], row[3], row[4], row[5], row[7], row[8])
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

    # ============ Two-Factor Authentication ============

    def enable_2fa(self, user_id):
        """Enable 2FA for a user."""
        if not HAS_2FA:
            logger.error("2FA libraries not installed")
            return None

        try:
            # Generate secret
            secret = pyotp.random_base32()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET otp_secret = ?, otp_enabled = 1
                WHERE id = ?
            ''', (secret, user_id))
            conn.commit()
            conn.close()

            return secret
        except Exception as e:
            logger.error(f"Error enabling 2FA: {e}")
            return None

    def disable_2fa(self, user_id):
        """Disable 2FA for a user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET otp_secret = NULL, otp_enabled = 0
                WHERE id = ?
            ''', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error disabling 2FA: {e}")
            return False

    def verify_2fa(self, user_id, code):
        """Verify 2FA code."""
        if not HAS_2FA:
            return False

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT otp_secret FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            conn.close()

            if not row or not row[0]:
                return False

            totp = pyotp.TOTP(row[0])
            return totp.verify(code)
        except Exception as e:
            logger.error(f"Error verifying 2FA: {e}")
            return False

    def get_2fa_qr(self, user_id, username):
        """Get QR code for 2FA setup."""
        if not HAS_2FA:
            return None

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT otp_secret FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            conn.close()

            if not row or not row[0]:
                return None

            # Generate QR code
            totp = pyotp.TOTP(row[0])
            uri = totp.provisioning_uri(username, issuer_name="UBP")

            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(uri)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert to base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            return img_str
        except Exception as e:
            logger.error(f"Error getting QR code: {e}")
            return None


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
            request.user = user
            return func(*args, **kwargs)
        return jsonify({"error": "Invalid or missing API key"}), 401
    return wrapper


# ============ JWT Token Generation ============

def generate_jwt_token(user_id, role='user'):
    """Generate a JWT token for a user."""
    try:
        import jwt
        payload = {
            'user_id': user_id,
            'role': role,
            'exp': datetime.utcnow() + timedelta(seconds=JWT_EXPIRY)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    except ImportError:
        return None


def verify_jwt_token(token):
    """Verify a JWT token."""
    try:
        import jwt
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except ImportError:
        return None


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


# ============ Two-Factor Authentication Routes ============

@auth_bp.route('/setup-2fa')
@login_required
def setup_2fa():
    """Setup 2FA page."""
    if not HAS_2FA:
        flash('2FA libraries not installed. Please install pyotp and qrcode.', 'danger')
        return redirect(url_for('auth.profile'))

    user_manager = get_user_manager()
    secret = user_manager.enable_2fa(current_user.id)
    if not secret:
        flash('Failed to enable 2FA', 'danger')
        return redirect(url_for('auth.profile'))

    qr_code = user_manager.get_2fa_qr(current_user.id, current_user.username)
    return render_template('setup_2fa.html', secret=secret, qr_code=qr_code)


@auth_bp.route('/verify-2fa', methods=['POST'])
@login_required
def verify_2fa():
    """Verify 2FA code."""
    code = request.form.get('code')
    if not code:
        flash('Please enter your 2FA code', 'danger')
        return redirect(url_for('auth.setup_2fa'))

    user_manager = get_user_manager()
    if user_manager.verify_2fa(current_user.id, code):
        flash('2FA enabled successfully!', 'success')
        return redirect(url_for('auth.profile'))
    else:
        flash('Invalid 2FA code. Please try again.', 'danger')
        return redirect(url_for('auth.setup_2fa'))


@auth_bp.route('/disable-2fa', methods=['POST'])
@login_required
def disable_2fa():
    """Disable 2FA."""
    user_manager = get_user_manager()
    if user_manager.disable_2fa(current_user.id):
        flash('2FA disabled successfully', 'success')
    else:
        flash('Failed to disable 2FA', 'danger')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password."""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not current_password or not new_password:
        flash('Please fill in all fields', 'danger')
        return redirect(url_for('auth.profile'))

    if new_password != confirm_password:
        flash('Passwords do not match', 'danger')
        return redirect(url_for('auth.profile'))

    if len(new_password) < 8:
        flash('Password must be at least 8 characters', 'danger')
        return redirect(url_for('auth.profile'))

    user_manager = get_user_manager()
    user = user_manager.get_user_by_id(current_user.id)

    if not bcrypt.check_password_hash(user.password_hash, current_password):
        flash('Current password is incorrect', 'danger')
        return redirect(url_for('auth.profile'))

    new_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')

    conn = sqlite3.connect(user_manager.db_path)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_hash, current_user.id))
    conn.commit()
    conn.close()

    flash('Password changed successfully!', 'success')
    return redirect(url_for('auth.profile'))


###############################################################################
# End of File
###############################################################################