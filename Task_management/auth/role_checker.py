from fastapi import Depends, HTTPException, status
from auth.auth_bearer import JWTBearer
from utils.decode_access_token import decode_access_token

def RoleChecker(allowed_roles: list[str]):
    def role_checker(token: str = Depends(JWTBearer())):
        payload = decode_access_token(token)
        user_role = payload.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )
        return payload
    return role_checker
