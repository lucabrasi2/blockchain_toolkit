"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
web.mailer

Purpose
-------
Email notification system for UBP.

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

from flask_mail import Mail, Message
from flask import current_app
from datetime import datetime
import threading

from core.logger import get_logger

logger = get_logger(__name__)

# Initialize mail
mail = Mail()


def send_async_email(app, msg):
    """Send email asynchronously."""
    with app.app_context():
        mail.send(msg)
        logger.info(f"Email sent to {msg.recipients}")


def send_email(to, subject, body, html=None):
    """
    Send an email.

    Parameters
    ----------
    to : str or list
        Recipient email address(es).
    subject : str
        Email subject.
    body : str
        Plain text body.
    html : str, optional
        HTML body.
    """
    try:
        msg = Message(subject, recipients=[to] if isinstance(to, str) else to)
        msg.body = body
        if html:
            msg.html = html

        # Send asynchronously
        app = current_app._get_current_object()
        thr = threading.Thread(target=send_async_email, args=[app, msg])
        thr.start()
        logger.info(f"Email queued for {to}")
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False


def send_alert_email(to, title, message, blockchain=None, address=None, severity="info"):
    """
    Send an alert email.

    Parameters
    ----------
    to : str
        Recipient email.
    title : str
        Alert title.
    message : str
        Alert message.
    blockchain : str, optional
        Blockchain name.
    address : str, optional
        Address involved.
    severity : str
        'info', 'warning', 'critical'
    """
    severity_colors = {
        'info': 'blue',
        'warning': 'orange',
        'critical': 'red',
    }
    color = severity_colors.get(severity, 'blue')

    subject = f"[UBP] {severity.upper()}: {title}"

    body = f"""
UBP Alert - {title}

Severity: {severity.upper()}
Message: {message}

Blockchain: {blockchain or 'N/A'}
Address: {address or 'N/A'}

Timestamp: {datetime.utcnow().isoformat()}

---
Universal Blockchain Platform
"""

    html = f"""
<!DOCTYPE html>
<html>
<head><style>
    body {{ font-family: Arial, sans-serif; padding: 20px; }}
    .alert {{ padding: 15px; border-left: 4px solid {color}; background: #f8f9fa; }}
    .severity-{severity} {{ border-left-color: {color}; }}
    .header {{ font-size: 20px; font-weight: bold; }}
    .details {{ margin-top: 10px; }}
</style></head>
<body>
    <div class="alert severity-{severity}">
        <div class="header">UBP Alert: {title}</div>
        <div><strong>Severity:</strong> {severity.upper()}</div>
        <div><strong>Message:</strong> {message}</div>
        <div class="details">
            <div><strong>Blockchain:</strong> {blockchain or 'N/A'}</div>
            <div><strong>Address:</strong> {address or 'N/A'}</div>
            <div><strong>Timestamp:</strong> {datetime.utcnow().isoformat()}</div>
        </div>
    </div>
</body>
</html>
    """

    return send_email(to, subject, body, html)


def send_welcome_email(to, username):
    """Send welcome email to new user."""
    subject = "Welcome to Universal Blockchain Platform!"

    body = f"""
Welcome {username}!

Thank you for joining the Universal Blockchain Platform (UBP).

Your account has been created successfully. You can now:

• Inspect wallets on Ethereum, Bitcoin, and TRON
• Analyze smart contracts and tokens
• Explore blocks and transactions
• Validate blockchain nodes
• Track your inspection history

To get started, log in at:
http://localhost:5000/auth/login

For support, please contact us at support@ubp.com.

---
Universal Blockchain Platform Team
"""

    html = f"""
<!DOCTYPE html>
<html>
<head><style>
    body {{ font-family: Arial, sans-serif; padding: 20px; }}
    .header {{ font-size: 24px; font-weight: bold; color: #6c5ce7; }}
    .welcome {{ margin: 20px 0; }}
</style></head>
<body>
    <div class="header">🌐 Universal Blockchain Platform</div>
    <div class="welcome">
        <p>Welcome <strong>{username}</strong>!</p>
        <p>Thank you for joining the Universal Blockchain Platform (UBP).</p>
        <p>Your account has been created successfully. You can now:</p>
        <ul>
            <li>Inspect wallets on Ethereum, Bitcoin, and TRON</li>
            <li>Analyze smart contracts and tokens</li>
            <li>Explore blocks and transactions</li>
            <li>Validate blockchain nodes</li>
            <li>Track your inspection history</li>
        </ul>
        <p>To get started, <a href="http://localhost:5000/auth/login">log in here</a>.</p>
        <p>For support, please contact us at support@ubp.com.</p>
    </div>
    <hr>
    <div style="color: #666; font-size: 12px;">
        Universal Blockchain Platform (UBP) v2.0.0
    </div>
</body>
</html>
    """

    return send_email(to, subject, body, html)


def send_password_reset_email(to, username, reset_token):
    """Send password reset email."""
    subject = "Password Reset - Universal Blockchain Platform"

    body = f"""
Hello {username},

We received a request to reset your password for your UBP account.

To reset your password, click the link below:
http://localhost:5000/auth/reset-password?token={reset_token}

This link will expire in 1 hour.

If you did not request a password reset, please ignore this email.

---
Universal Blockchain Platform Team
"""

    html = f"""
<!DOCTYPE html>
<html>
<head><style>
    body {{ font-family: Arial, sans-serif; padding: 20px; }}
    .header {{ font-size: 24px; font-weight: bold; color: #6c5ce7; }}
</style></head>
<body>
    <div class="header">🌐 Universal Blockchain Platform</div>
    <p>Hello <strong>{username}</strong>,</p>
    <p>We received a request to reset your password for your UBP account.</p>
    <p>To reset your password, click the link below:</p>
    <p><a href="http://localhost:5000/auth/reset-password?token={reset_token}">Reset Password</a></p>
    <p>This link will expire in 1 hour.</p>
    <p>If you did not request a password reset, please ignore this email.</p>
    <hr>
    <div style="color: #666; font-size: 12px;">Universal Blockchain Platform (UBP) v2.0.0</div>
</body>
</html>
    """

    return send_email(to, subject, body, html)


###############################################################################
# End of File
###############################################################################
