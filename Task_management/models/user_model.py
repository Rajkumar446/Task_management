from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum

class UserRoleEnum(str, enum.Enum):
    team_lead = "team_lead"
    developer = "developer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRoleEnum), nullable=False)

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    tasks_assigned = relationship("Task", back_populates="assigned_user", cascade="all, delete-orphan")
