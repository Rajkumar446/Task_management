from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.task_model import TaskStatus

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.todo
    due_date: Optional[datetime] = None  # added due_date
    project_id: int
    assigned_user_id: Optional[int] = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    due_date: Optional[datetime] = None  # added due_date
    project_id: int
    assigned_user_id: Optional[int] = None

    class Config:
        from_attributes = True
