from fastapi import APIRouter, HTTPException, status, Query, Depends, Request
from sqlalchemy.orm import Session
from typing import Tuple
from database import get_db
from models import User, Task
from schemas.user_schema import UserCreate, UserLogin, UserOut
from schemas.task_schema import TaskOut
from auth.jwt_handler import hash_password, verify_password, create_access_token
from middleware.auth_middleware import (
    get_current_user_info, 
    get_optional_user_info,
    require_team_lead, 
    require_developer,
    require_any_role
)


router = APIRouter(prefix="/users", tags=["Users"])

# User registration

@router.post("/register")
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pw,
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "id": new_user.id,
        "email": new_user.email,
        "role": new_user.role
    }

# User login

@router.post("/login")
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"user_id": user.id, "role": user.role.value})
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.value,
        "access_token": token,
        "token_type": "bearer"
    }

# Get all users (team_lead: all, developer: only self)
@router.get("/", response_model=list[UserOut])
def get_all_users(
    user_info: Tuple[int, str, User] = Depends(require_any_role),
    db: Session = Depends(get_db)
):
    user_id, role, user = user_info
    
    if role == "developer":
        # Developers can only see their own data
        return [user]
    else:  # team_lead
        # Team leads can see all users
        return db.query(User).all()



# Get current user details and assigned tasks
@router.get("/me")
def get_current_user_details(
    user_info: Tuple[int, str, User] = Depends(require_any_role),
    db: Session = Depends(get_db)
):
    user_id, role, user = user_info
    
    tasks = db.query(Task).filter(Task.assigned_user_id == user_id).all()
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "tasks_assigned": [TaskOut.from_orm(task) for task in tasks]
    }

# Get user by id (authenticated users only)
@router.get("/{user_id}")
def get_user_by_id(
    user_id: int, 
    user_info: Tuple[int, str, User] = Depends(require_any_role),
    db: Session = Depends(get_db)
):
    current_user_id, current_role, current_user = user_info
    
    # Developers can only view their own profile
    if current_role == "developer" and current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Developers can only view their own profile"
        )
    
    user_obj = db.query(User).filter(User.id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {
        "id": user_obj.id,
        "email": user_obj.email,
        "role": user_obj.role
    }
