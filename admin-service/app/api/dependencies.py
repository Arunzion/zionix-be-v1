from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.AUTH_SERVICE_URL}/api/v1/auth/token")

# Database dependency
def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting a database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Token validation dependency
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Validate the access token and return the current user
    
    This is a simplified implementation. In a real-world scenario,
    you would likely make an API call to the auth service to validate the token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Return the user ID from the token
        return {"user_id": user_id}
    except JWTError:
        raise credentials_exception