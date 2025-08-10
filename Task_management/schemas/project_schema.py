from pydantic import BaseModel
from typing import List, Optional
from schemas.task_schema import TaskOut

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class ProjectOut(ProjectBase):
    id: int
    tasks: List[TaskOut] = []

    class Config:
        from_attributes = True
