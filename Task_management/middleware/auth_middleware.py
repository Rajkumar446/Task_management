from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, Tuple
from database import get_db
from models.user_model import User, UserRoleEnum
from auth.jwt_handler import verify_access_token
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware:
    """
    Middleware class for extracting user information from access tokens
    """
    
    def __init__(self):
        self.security = HTTPBearer(auto_error=False)
    
    async def get_current_user_from_token(
        self, 
        request: Request,
        db: Session = Depends(get_db)
    ) -> Optional[Tuple[int, str, User]]:
        """
        Extract user ID, role, and user object from access token
        Returns: (user_id, role, user_object) or None if no valid token
        """
        try:
            # Get authorization header
            authorization: HTTPAuthorizationCredentials = await self.security(request)
            
            if not authorization:
                return None
                
            if authorization.scheme.lower() != "bearer":
                return None
                
            token = authorization.credentials
            
            # Verify and decode token
            payload = verify_access_token(token)
            if not payload:
                return None
                
            user_id = payload.get("user_id")
            role = payload.get("role")
            
            if not user_id or not role:
                return None
                
            # Get user from database to ensure they still exist
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
                
            # Ensure role in token matches database role
            if user.role.value != role:
                return None
                
            return user_id, role, user
            
        except Exception as e:
            logger.error(f"Error in auth middleware: {str(e)}")
            return None

# Global instance
auth_middleware = AuthMiddleware()

async def get_current_user_info(
    request: Request,
    db: Session = Depends(get_db)
) -> Tuple[int, str, User]:
    """
    Dependency to get current authenticated user information
    Raises 401 if no valid token found
    """
    user_info = await auth_middleware.get_current_user_from_token(request, db)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_info

async def get_optional_user_info(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[Tuple[int, str, User]]:
    """
    Dependency to optionally get current user information
    Returns None if no valid token (doesn't raise exception)
    """
    return await auth_middleware.get_current_user_from_token(request, db)

def require_roles(allowed_roles: list[str]):
    """
    Decorator to require specific roles for an endpoint
    """
    async def role_dependency(
        user_info: Tuple[int, str, User] = Depends(get_current_user_info)
    ) -> Tuple[int, str, User]:
        user_id, role, user = user_info
        
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        
        return user_info
    
    # Add security metadata for OpenAPI docs
    role_dependency.__annotations__["return"] = Tuple[int, str, User]
    return role_dependency

# Convenience dependencies for specific roles
require_team_lead = require_roles(["team_lead"])
require_developer = require_roles(["developer"])
require_any_role = require_roles(["team_lead", "developer"])

