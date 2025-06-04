# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from . import token
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
#
#
# def get_current_user(data: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#
#     return token.verify_token(data, credentials_exception)

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    print("Token received from frontend:", token)
    try:
        payload = jwt.decode(token, "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7", algorithms=["HS256"])

        email: str = payload.get("sub")
        role: str = payload.get("role")
        print("Email:", email)
        print("Role:", role)
        if email is None or role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token!")
        return {"email": email, "role": role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
