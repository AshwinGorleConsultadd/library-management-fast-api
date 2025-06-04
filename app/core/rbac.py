from fastapi import Depends, HTTPException, status
from ..oauth2 import get_current_user

def role_required(allowed_roles: list[str]):
    def wrapper(user: dict = Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: insufficient permissions"
            )
        return user
    return wrapper
