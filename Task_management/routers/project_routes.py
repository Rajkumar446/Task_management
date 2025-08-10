
from fastapi import APIRouter, HTTPException, status, Query, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Tuple
from database import get_db
from models.project_model import Project
from models.user_model import User
from schemas.project_schema import ProjectCreate, ProjectOut
from middleware.auth_middleware import (
    get_current_user_info, 
    require_team_lead, 
    require_any_role
)

router = APIRouter(prefix="/projects", tags=["projects"])


# Team lead: CRUD, developer: only read their own projects
@router.post(
    "/", 
    response_model=ProjectOut, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[],
    summary="Create a new project",
    description="Only team leads can create projects. Requires JWT authentication."
)
def create_project(
    project: ProjectCreate,
    user_info: Tuple[int, str, User] = Depends(require_team_lead),
    db: Session = Depends(get_db)
):
    user_id, role, user = user_info
    
    db_project = Project(**project.dict(), owner_id=user_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=List[ProjectOut])
def read_projects(
    user_info: Tuple[int, str, User] = Depends(require_any_role),
    db: Session = Depends(get_db)
):
    user_id, role, user = user_info
    
    if role == "developer":
        # Developers can only see their own projects
        return db.query(Project).filter(Project.owner_id == user_id).all()
    else:  # team_lead
        # Team leads can see all projects
        return db.query(Project).all()

# GET /projects/{id} – project details with all tasks
@router.get("/{project_id}")
def read_project(
    project_id: int,
    user_info: Tuple[int, str, User] = Depends(require_any_role),
    db: Session = Depends(get_db)
):
    user_id, role, user = user_info
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Developers can only view their own projects
    if role == "developer" and project.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this project")
        
    # Get all tasks for this project
    from models.task_model import Task
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    return {
        "project": project,
        "tasks": tasks
    }

@router.patch("/{project_id}")
def patch_project(
    project_id: int,
    updated_fields: dict,
    user_info: Tuple[int, str, User] = Depends(require_team_lead),
    db: Session = Depends(get_db)
):
    user_id, role, user = user_info
    
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    for key, value in updated_fields.items():
        if hasattr(project, key):
            setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project

@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    updated_project: ProjectCreate,
    user_info: Tuple[int, str, User] = Depends(require_team_lead),
    db: Session = Depends(get_db)
):
    user_id, role, user = user_info
    
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    for key, value in updated_project.dict().items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    user_info: Tuple[int, str, User] = Depends(require_team_lead),
    db: Session = Depends(get_db)
):
    user_id, role, user = user_info
    
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    db.delete(project)
    db.commit()
    return None
