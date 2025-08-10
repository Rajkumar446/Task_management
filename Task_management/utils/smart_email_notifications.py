"""
Smart Email Notifications - Automatic email triggers based on task events and schedules
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user_model import User
from models.task_model import Task, TaskStatus
from models.project_model import Project
from utils.email_queue import queue_email
import logging

logger = logging.getLogger(__name__)

def send_task_assignment_email(task: Task, db: Session):
    """
    Send email immediately when a task is assigned to a user
    """
    if not task.assigned_user_id:
        return
    
    assigned_user = db.query(User).filter(User.id == task.assigned_user_id).first()
    if not assigned_user:
        return
    
    project = db.query(Project).filter(Project.id == task.project_id).first()
    project_name = project.name if project else "Unknown Project"
    
    subject = "🎯 New Task Assigned"
    body = f"""Hello {assigned_user.email},

You have been assigned a new task:

📋 Task: {task.title}
📝 Description: {task.description}
🏢 Project: {project_name}
📅 Status: {task.status.value}
{f'⏰ Due Date: {task.due_date}' if hasattr(task, 'due_date') and task.due_date else ''}

Please log in to your task management dashboard to view details.

Best regards,
Task Management System"""
    
    queue_email(
        to_email=assigned_user.email,
        subject=subject,
        body=body
    )
    logger.info(f"Task assignment email queued for {assigned_user.email}")

def send_task_status_change_email(task: Task, old_status: TaskStatus, db: Session):
    """
    Send email when task status changes
    """
    if not task.assigned_user_id:
        return
    
    assigned_user = db.query(User).filter(User.id == task.assigned_user_id).first()
    if not assigned_user:
        return
    
    project = db.query(Project).filter(Project.id == task.project_id).first()
    project_name = project.name if project else "Unknown Project"
    
    status_emoji = {
        'todo': '📝',
        'in_progress': '🔄', 
        'done': '✅',
        'blocked': '🚫'
    }
    
    subject = f"📊 Task Status Updated: {task.title}"
    body = f"""Hello {assigned_user.email},

Your task status has been updated:

📋 Task: {task.title}
🏢 Project: {project_name}
📊 Status: {status_emoji.get(old_status.value, '📝')} {old_status.value} → {status_emoji.get(task.status.value, '📝')} {task.status.value}

{f'⏰ Due Date: {task.due_date}' if hasattr(task, 'due_date') and task.due_date else ''}

Keep up the great work!

Best regards,
Task Management System"""
    
    queue_email(
        to_email=assigned_user.email,
        subject=subject,
        body=body
    )
    logger.info(f"Task status change email queued for {assigned_user.email}")

def send_task_reassignment_email(task: Task, old_user_id: int, db: Session):
    """
    Send email when task is reassigned to a different user
    """
    # Email to new assignee
    send_task_assignment_email(task, db)
    
    # Email to previous assignee
    if old_user_id:
        old_user = db.query(User).filter(User.id == old_user_id).first()
        if old_user:
            subject = "📤 Task Reassigned"
            body = f"""Hello {old_user.email},

The following task has been reassigned to another team member:

📋 Task: {task.title}
📝 Description: {task.description}

Thank you for your previous work on this task.

Best regards,
Task Management System"""
            
            queue_email(
                to_email=old_user.email,
                subject=subject,
                body=body
            )
            logger.info(f"Task reassignment email queued for previous assignee {old_user.email}")

def check_and_send_due_date_reminders():
    """
    Check for tasks due today, tomorrow, or overdue and send reminder emails
    Called by scheduler
    """
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        today = now.date()
        tomorrow = now + timedelta(days=1)
        
        # Tasks due TODAY (due date reminder)
        tasks_due_today = db.query(Task).filter(
            Task.due_date == today,
            Task.status != TaskStatus.done,
            Task.assigned_user_id.isnot(None)
        ).all()
        
        for task in tasks_due_today:
            send_due_today_reminder(task, db)
        
        # Tasks due tomorrow (1 day advance reminder)
        tasks_due_tomorrow = db.query(Task).filter(
            Task.due_date == tomorrow.date(),
            Task.status != TaskStatus.done,
            Task.assigned_user_id.isnot(None)
        ).all()
        
        for task in tasks_due_tomorrow:
            send_due_tomorrow_reminder(task, db)
        
        # Overdue tasks (daily reminder)
        overdue_tasks = db.query(Task).filter(
            Task.due_date < today,
            Task.status != TaskStatus.done,
            Task.assigned_user_id.isnot(None)
        ).all()
        
        for task in overdue_tasks:
            send_overdue_reminder(task, db)
            
        logger.info(f"Processed {len(tasks_due_today)} due today, {len(tasks_due_tomorrow)} due tomorrow, {len(overdue_tasks)} overdue tasks")
        
    except Exception as e:
        logger.error(f"Error in due date reminder check: {e}")
    finally:
        db.close()

def send_due_today_reminder(task: Task, db: Session):
    """
    Send reminder email for tasks due today
    """
    assigned_user = db.query(User).filter(User.id == task.assigned_user_id).first()
    if not assigned_user:
        return
    
    project = db.query(Project).filter(Project.id == task.project_id).first()
    project_name = project.name if project else "Unknown Project"
    
    subject = "🚨 Task Due TODAY - Action Required"
    body = f"""Hello {assigned_user.email},

⚠️ URGENT: You have a task due TODAY that requires immediate attention!

📋 Task: {task.title}
📝 Description: {task.description}
🏢 Project: {project_name}
📅 Due Date: {task.due_date} (TODAY)
📊 Current Status: {task.status.value}

Please complete this task today to avoid it becoming overdue.

Best regards,
Task Management System"""
    
    queue_email(
        to_email=assigned_user.email,
        subject=subject,
        body=body
    )
    logger.info(f"Due today reminder email queued for {assigned_user.email}")

def send_due_tomorrow_reminder(task: Task, db: Session):
    """
    Send reminder email for tasks due tomorrow
    """
    assigned_user = db.query(User).filter(User.id == task.assigned_user_id).first()
    if not assigned_user:
        return
    
    project = db.query(Project).filter(Project.id == task.project_id).first()
    project_name = project.name if project else "Unknown Project"
    
    subject = "⏰ Task Due Tomorrow - Reminder"
    body = f"""Hello {assigned_user.email},

🚨 Friendly reminder: You have a task due tomorrow!

📋 Task: {task.title}
📝 Description: {task.description}
🏢 Project: {project_name}
📅 Due Date: {task.due_date}
📊 Current Status: {task.status.value}

Please ensure you complete this task on time.

Best regards,
Task Management System"""
    
    queue_email(
        to_email=assigned_user.email,
        subject=subject,
        body=body
    )
    logger.info(f"Due tomorrow reminder sent to {assigned_user.email} for task: {task.title}")

def send_overdue_reminder(task: Task, db: Session):
    """
    Send reminder email for overdue tasks
    """
    assigned_user = db.query(User).filter(User.id == task.assigned_user_id).first()
    if not assigned_user:
        return
    
    project = db.query(Project).filter(Project.id == task.project_id).first()
    project_name = project.name if project else "Unknown Project"
    
    days_overdue = (datetime.utcnow().date() - task.due_date).days
    
    subject = f"🚨 OVERDUE: Task {days_overdue} day(s) past due"
    body = f"""Hello {assigned_user.email},

⚠️ URGENT: You have an overdue task that needs immediate attention!

📋 Task: {task.title}
📝 Description: {task.description}
🏢 Project: {project_name}
📅 Due Date: {task.due_date}
🚨 Days Overdue: {days_overdue}
📊 Current Status: {task.status.value}

Please prioritize this task and update its status as soon as possible.

Best regards,
Task Management System"""
    
    queue_email(
        to_email=assigned_user.email,
        subject=subject,
        body=body
    )
    logger.info(f"Overdue reminder sent to {assigned_user.email} for task: {task.title} ({days_overdue} days overdue)")

def send_weekly_summary_to_team_leads():
    """
    Send weekly summary to team leads
    Called by scheduler every week
    """
    db = SessionLocal()
    try:
        team_leads = db.query(User).filter(User.role == "team_lead").all()
        
        for team_lead in team_leads:
            # Get projects owned by this team lead
            projects = db.query(Project).filter(Project.owner_id == team_lead.id).all()
            
            if not projects:
                continue
            
            # Collect task statistics
            total_tasks = 0
            completed_tasks = 0
            overdue_tasks = 0
            due_this_week = 0
            
            project_summaries = []
            
            for project in projects:
                tasks = db.query(Task).filter(Task.project_id == project.id).all()
                project_total = len(tasks)
                project_completed = len([t for t in tasks if t.status == TaskStatus.done])
                project_overdue = len([t for t in tasks if hasattr(t, 'due_date') and t.due_date and t.due_date < datetime.utcnow().date() and t.status != TaskStatus.done])
                
                total_tasks += project_total
                completed_tasks += project_completed
                overdue_tasks += project_overdue
                
                project_summaries.append(f"  • {project.name}: {project_completed}/{project_total} completed, {project_overdue} overdue")
            
            if total_tasks == 0:
                continue
            
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            subject = f"📊 Weekly Team Summary - {completion_rate:.1f}% Completion Rate"
            body = f"""Hello {team_lead.email},

Here's your weekly team summary:

📈 OVERVIEW:
• Total Tasks: {total_tasks}
• Completed: {completed_tasks} ({completion_rate:.1f}%)
• Overdue: {overdue_tasks}
• In Progress: {total_tasks - completed_tasks - overdue_tasks}

🏢 PROJECT BREAKDOWN:
{chr(10).join(project_summaries)}

{f'⚠️  Action Required: {overdue_tasks} tasks are overdue and need attention.' if overdue_tasks > 0 else '✅ Great job! No overdue tasks.'}

Best regards,
Task Management System"""
            
            queue_email(
                to_email=team_lead.email,
                subject=subject,
                body=body
            )
            logger.info(f"Weekly summary sent to team lead: {team_lead.email}")
            
    except Exception as e:
        logger.error(f"Error in weekly summary: {e}")
    finally:
        db.close()
