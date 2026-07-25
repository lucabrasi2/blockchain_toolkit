"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
web.permissions

Purpose
-------
User roles and permissions system.

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

from functools import wraps
from flask import jsonify, flash, redirect, url_for
from flask_login import current_user


class Role:
    """User roles."""
    ADMIN = 'admin'
    USER = 'user'
    VIEWER = 'viewer'
    API = 'api'


class Permission:
    """Permission definitions."""
    VIEW_DASHBOARD = 'view_dashboard'
    VIEW_HISTORY = 'view_history'
    EXPORT_DATA = 'export_data'
    INSPECT_WALLET = 'inspect_wallet'
    INSPECT_CONTRACT = 'inspect_contract'
    MANAGE_USERS = 'manage_users'
    MANAGE_API_KEYS = 'manage_api_keys'
    VIEW_ANALYTICS = 'view_analytics'


# Role permissions mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_HISTORY,
        Permission.EXPORT_DATA,
        Permission.INSPECT_WALLET,
        Permission.INSPECT_CONTRACT,
        Permission.MANAGE_USERS,
        Permission.MANAGE_API_KEYS,
        Permission.VIEW_ANALYTICS,
    ],
    Role.USER: [
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_HISTORY,
        Permission.EXPORT_DATA,
        Permission.INSPECT_WALLET,
        Permission.INSPECT_CONTRACT,
        Permission.MANAGE_API_KEYS,
        Permission.VIEW_ANALYTICS,
    ],
    Role.VIEWER: [
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_HISTORY,
        Permission.VIEW_ANALYTICS,
    ],
    Role.API: [
        Permission.INSPECT_WALLET,
        Permission.INSPECT_CONTRACT,
        Permission.EXPORT_DATA,
    ],
}


def has_permission(permission):
    """Check if current user has a permission."""
    if not current_user.is_authenticated:
        return False
    
    role = getattr(current_user, 'role', Role.VIEWER)
    allowed = ROLE_PERMISSIONS.get(role, [])
    return permission in allowed


def require_permission(permission):
    """Decorator to require a permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not has_permission(permission):
                if request and request.is_json:
                    return jsonify({"error": "Permission denied"}), 403
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_role(role):
    """Decorator to require a role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"error": "Unauthorized"}), 401
            if getattr(current_user, 'role', Role.VIEWER) != role:
                return jsonify({"error": "Permission denied"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


###############################################################################
# End of File
###############################################################################
