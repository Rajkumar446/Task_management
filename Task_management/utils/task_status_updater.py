from datetime import datetime
from models.task_model import Task, TaskStatus
from database import SessionLocal
from utils.email_queue import queue_email
from models.user_model import User

def update_task_status_daily():
    db = SessionLocal()
    try:
        tasks = db.query(Task).filter(Task.status != TaskStatus.done).all()
        for task in tasks:
            if task.due_date and task.due_date < datetime.utcnow():
                if task.status != TaskStatus.pending:
                    old_status = task.status
                    task.status = TaskStatus.pending

                    # Send email notifying the assigned user about overdue status
                    if task.assigned_user_id:
                        assigned_user = db.query(User).filter(User.id == task.assigned_user_id).first()
                        if assigned_user:
                            queue_email(
                                to_email=assigned_user.email,
                                subject="Task Overdue Notification",
                                body=f"The task '{task.title}' is overdue. Please update its status."
                            )
            else:
                # Optionally reset status if not overdue and was pending
                if task.status == TaskStatus.pending:
                    task.status = TaskStatus.todo
        db.commit()
    finally:
        db.close()
