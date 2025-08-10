from pydantic import BaseModel, EmailStr
from enum import Enum

class UserRoleEnum(str, Enum):
    team_lead = "team_lead"
    developer = "developer"

# Used for creating/registering a new user
class UserCreate(BaseModel):
    email: EmailStr
    password: str              # plain password input (will be hashed in backend)
    role: UserRoleEnum

# Used for user login input
class UserLogin(BaseModel):
    email: EmailStr
    password: str              # plain password input

# Used for response/output (never expose hashed password)
class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: UserRoleEnum

    class Config:
        from_attributes = True
