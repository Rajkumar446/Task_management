# 📧 Email Viewing Guide - See Emails During Development

## 🎯 Where to See Emails

Your project sends emails when:
- ✅ Tasks are assigned to users
- ✅ Task status changes
- ✅ Daily summaries (scheduled)

Since you're in development mode (no SMTP credentials configured), emails are **logged locally** instead of actually sent.

## 🔍 3 Ways to View Sent Emails

### 1. 📱 **API Endpoints (Easiest)**
Use these endpoints in Swagger UI (`http://127.0.0.1:8000/docs`):

- **`GET /emails/sent`** - View all sent emails in JSON format
- **`GET /emails/test`** - Send a test email to yourself
- **`GET /emails/recent`** - Print recent emails to console
- **`DELETE /emails/clear`** - Clear email log

### 2. 🖥️ **Console Output (Real-time)**
Watch your terminal where the server is running. When emails are sent, you'll see:

```
============================================================
📧 EMAIL SENT (Development Mode)
============================================================
To: user@example.com
Subject: New Task Assigned
Time: 2025-08-09T21:16:05.123456
------------------------------------------------------------
Body:
You have been assigned a new task: My New Task
============================================================
```

### 3. 📁 **Log File**
Emails are saved to: `email_logs/sent_emails.json`

## 🧪 **Test Email System Right Now**

1. **Make sure you're authenticated** (login and use token)
2. **Send test email**: `GET /emails/test`
3. **View the email**: `GET /emails/sent`
4. **Check console**: Look at your terminal running the server

## 🚀 **Trigger Emails with Real Actions**

### Create a Task (Sends Email to Assignee)
```bash
POST /tasks/
{
  "title": "Test Task",
  "description": "This will send an email",
  "project_id": 1,
  "assigned_user_id": 2,  # Email sent to this user
  "status": "todo"
}
```

### Update Task Status (Sends Email)
```bash
PATCH /tasks/1
{
  "status": "in_progress"  # Email sent to assigned user
}
```

## 📊 **Example API Response**

When you call `GET /emails/sent`, you'll see:

```json
[
  {
    "timestamp": "2025-08-09T21:16:05.123456",
    "to": "developer@example.com",
    "subject": "New Task Assigned",
    "body": "You have been assigned a new task: My New Task",
    "status": "logged_for_development"
  }
]
```

## 🔧 **Production Setup**

To send real emails in production, set these environment variables:
```bash
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
```

## 💡 **Pro Tips**

- 📧 **Always check console** - emails print in real-time
- 🔄 **Use `/emails/test`** - quick way to verify system works  
- 📋 **Use `/emails/sent`** - see all emails in organized format
- 🗑️ **Use `/emails/clear`** - clean up when testing

Your email system is working perfectly - it's just showing you the emails locally for development! 🎯
