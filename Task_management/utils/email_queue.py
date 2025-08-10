import threading
import queue
import time
from utils.email_sender_dev import send_email
from database import SessionLocal
from models.user_model import User
from models.task_model import Task, TaskStatus
from models.project_model import Project
from datetime import datetime

# Global task queue
email_task_queue = queue.Queue()

def email_worker():
    while True:
        task = email_task_queue.get()
        if task is None:
            break
        try:
            send_email(**task)
        except Exception as e:
            print(f"Failed to send email: {e}")
        email_task_queue.task_done()

# Start the email worker thread
worker_thread = threading.Thread(target=email_worker, daemon=True)
worker_thread.start()

def queue_email(to_email: str, subject: str, body: str):
    email_task_queue.put({"to_email": to_email, "subject": subject, "body": body})

# Daily summary function (to be called by a scheduler like APScheduler)
def send_daily_summary():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            projects = db.query(Project).filter(Project.owner_id == user.id).all()
            completed_tasks = []
            pending_tasks = []
            overdue_tasks = []
            for project in projects:
                completed_tasks += db.query(Task).filter(
                    Task.project_id == project.id,
                    Task.status == TaskStatus.done,
                    Task.due_date <= datetime.utcnow()
                ).all()
                pending_tasks += db.query(Task).filter(
                    Task.project_id == project.id,
                    Task.status != TaskStatus.done,
                    Task.due_date > datetime.utcnow()
                ).all()
                overdue_tasks += db.query(Task).filter(
                    Task.project_id == project.id,
                    Task.status != TaskStatus.done,
                    Task.due_date <= datetime.utcnow()
                ).all()
            body = f"Hello {user.email},\n\n"
            if completed_tasks:
                completed_list = "\n".join([f"- {t.title} (Completed)" for t in completed_tasks])
                body += f"Completed tasks:\n{completed_list}\n\n"
            if pending_tasks:
                pending_list = "\n".join([f"- {t.title} (Pending, Due: {t.due_date})" for t in pending_tasks])
                body += f"Pending tasks:\n{pending_list}\n\n"
            if overdue_tasks:
                overdue_list = "\n".join([f"- {t.title} (Overdue, Due: {t.due_date})" for t in overdue_tasks])
                body += f"Overdue tasks:\n{overdue_list}\n\n"
            if completed_tasks or pending_tasks or overdue_tasks:
                queue_email(
                    to_email=user.email,
                    subject="Daily Task Summary",
                    body=body
                )
    finally:
        db.close()
