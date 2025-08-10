# utils/filters.py
from sqlalchemy.orm import Query
from typing import Optional
from datetime import datetime

def apply_task_filters(
    query: Query,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[datetime] = None,
    project_id: Optional[int] = None
) -> Query:
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    if due_date:
        query = query.filter(Task.due_date <= due_date)
    if project_id:
        query = query.filter_by(project_id=project_id)
    return query
