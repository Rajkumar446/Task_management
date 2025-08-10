"""
Development Email Viewer - For Testing Email Functionality
This module replaces real email sending with console output and file logging for development.
"""
import os
import json
from datetime import datetime
from typing import Dict, List

# Directory to store email logs
EMAIL_LOG_DIR = "email_logs"
EMAIL_LOG_FILE = os.path.join(EMAIL_LOG_DIR, "sent_emails.json")

def ensure_email_log_dir():
    """Create email log directory if it doesn't exist"""
    if not os.path.exists(EMAIL_LOG_DIR):
        os.makedirs(EMAIL_LOG_DIR)

def send_email_dev(to_email: str, subject: str, body: str):
    """
    Development email sender - logs emails instead of sending them
    """
    ensure_email_log_dir()
    
    # Create email record
    email_record = {
        "timestamp": datetime.now().isoformat(),
        "to": to_email,
        "subject": subject,
        "body": body,
        "status": "logged_for_development"
    }
    
    # Print to console
    print("\n" + "="*60)
    print("📧 EMAIL SENT (Development Mode)")
    print("="*60)
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(f"Time: {email_record['timestamp']}")
    print("-" * 60)
    print(f"Body:\n{body}")
    print("="*60 + "\n")
    
    # Save to file
    try:
        # Load existing emails
        if os.path.exists(EMAIL_LOG_FILE):
            with open(EMAIL_LOG_FILE, 'r') as f:
                emails = json.load(f)
        else:
            emails = []
        
        # Add new email
        emails.append(email_record)
        
        # Save back to file
        with open(EMAIL_LOG_FILE, 'w') as f:
            json.dump(emails, f, indent=2)
            
    except Exception as e:
        print(f"Warning: Could not save email to log file: {e}")

def get_sent_emails(limit: int = 10) -> List[Dict]:
    """
    Retrieve last sent emails for viewing
    """
    try:
        if os.path.exists(EMAIL_LOG_FILE):
            with open(EMAIL_LOG_FILE, 'r') as f:
                emails = json.load(f)
            return emails[-limit:] if emails else []
    except Exception as e:
        print(f"Error reading email log: {e}")
    return []

def clear_email_log():
    """
    Clear all logged emails
    """
    try:
        if os.path.exists(EMAIL_LOG_FILE):
            os.remove(EMAIL_LOG_FILE)
        print("Email log cleared!")
    except Exception as e:
        print(f"Error clearing email log: {e}")

def print_recent_emails(count: int = 5):
    """
    Print recent emails to console
    """
    emails = get_sent_emails(count)
    if not emails:
        print("No emails found in log.")
        return
    
    print(f"\n📧 Last {len(emails)} Email(s) Sent:")
    print("="*50)
    
    for i, email in enumerate(emails, 1):
        print(f"\n{i}. [{email['timestamp']}]")
        print(f"   To: {email['to']}")
        print(f"   Subject: {email['subject']}")
        print(f"   Body Preview: {email['body'][:100]}...")
        print("-" * 50)
