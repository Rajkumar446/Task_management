# utils/email_sender_dev.py - Development Email Sender
import os
from utils.dev_email_viewer import send_email_dev

# Check if we're in development mode (no SMTP credentials configured)
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
IS_DEVELOPMENT = not (SMTP_USER and SMTP_PASS)

def send_email(to_email: str, subject: str, body: str):
    """
    Smart email sender - uses development mode if no SMTP credentials are configured
    """
    if IS_DEVELOPMENT:
        # Development mode - log emails to console and file
        send_email_dev(to_email, subject, body)
    else:
        # Production mode - send real emails
        from utils.email_sender import send_email as send_real_email
        send_real_email(to_email, subject, body)
