from fastapi import APIRouter, HTTPException, status, Query, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Tuple
from database import get_db
from models.task_model import Task, TaskStatus
from models.user_model import User
from schemas.task_schema import TaskCreate, TaskOut
from utils.email_queue import queue_email
from utils.smart_email_notifications import (
    send_task_assignment_email, 
    send_task_status_change_email, 
    send_task_reassignment_email
)
from middleware.auth_middleware import (
    get_current_user_info, 
    require_team_lead, 
    require_any_role
)

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    user_info: Tuple[int, str, User] = Depends(require_team_lead),
    db: Session = Depends(get_db)
):
    user_id, role, user = user_info

    # Ensure status is TaskStatus enum
    status_value = TaskStatus(task.status) if hasattr(task, "status") and task.status else TaskStatus.todo

    db_task = Task(
        title=task.title,
        description=task.description,
        status=status_value,
        project_id=task.project_id,
        assigned_user_id=task.assigned_user_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # 📧 SMART EMAIL: Automatically send assignment email
    if db_task.assigned_user_id:
        send_task_assignment_email(db_task, db)
    
    return db_task


@router.get("/", response_model=List[TaskOut])
def read_tasks(
    user_info: Tuple[int, str, User] = Depends(require_any_role),
    db: Session = Depends(get_db)
):
    user_id, role, user = user_info
    
    if role == "developer":
        # Developers can only see their assigned tasks
        return db.query(Task).filter(Task.assigned_user_id == user_id).all()
    else:  # team_lead
        # Team leads can see all tasks
        return db.query(Task).all()


@router.get("/{task_id}", response_model=TaskOut)
def read_task(
    task_id: int,
    user_info: Tuple[int, str, User] = Depends(require_any_role),
    db: Session = Depends(get_db)
):
    user_id, role, user = user_info
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    # Developers can only view their assigned tasks
    if role == "developer" and task.assigned_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this task")
        
    return task


@router.patch("/{task_id}", response_model=TaskOut)
def patch_task(
    task_id: int,
    updated_fields: dict,
    user_info: Tuple[int, str, User] = Depends(require_any_role),
    db: Session = Depends(get_db)
):
    user_id, role, user = user_info
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    # Developers can only update their assigned tasks
    if role == "developer" and task.assigned_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")

    old_assignee = task.assigned_user_id
    old_status = task.status

    for key, value in updated_fields.items():
        if key == "status":
            value = TaskStatus(value)
        if hasattr(task, key):
            setattr(task, key, value)

    db.commit()
    db.refresh(task)

    # 📧 SMART EMAIL: Handle assignment changes
    if task.assigned_user_id != old_assignee:
        send_task_reassignment_email(task, old_assignee, db)

    # 📧 SMART EMAIL: Handle status changes
    if task.status != old_status:
        send_task_status_change_email(task, old_status, db)

    return task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    updated_task: TaskCreate,
    user_info: Tuple[int, str, User] = Depends(require_any_role),
    db: Session = Depends(get_db)
):
    user_id, role, user = user_info
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    # Developers can only update their assigned tasks
    if role == "developer" and task.assigned_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")

    old_assignee = task.assigned_user_id
    old_status = task.status

    # Convert status string to enum
    status_value = TaskStatus(updated_task.status) if updated_task.status else task.status

    task.title = updated_task.title
    task.description = updated_task.description
    task.status = status_value
    task.project_id = updated_task.project_id
    task.assigned_user_id = updated_task.assigned_user_id

    db.commit()
    db.refresh(task)

    # 📧 SMART EMAIL: Handle assignment changes
    if task.assigned_user_id != old_assignee:
        send_task_reassignment_email(task, old_assignee, db)

    # 📧 SMART EMAIL: Handle status changes
    if task.status != old_status:
        send_task_status_change_email(task, old_status, db)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    user_info: Tuple[int, str, User] = Depends(require_team_lead),
    db: Session = Depends(get_db)
):
    user_id, role, user = user_info
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    db.delete(task)
    db.commit()
    return None
