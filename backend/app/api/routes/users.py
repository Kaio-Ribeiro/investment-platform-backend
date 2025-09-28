from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt
from app.core.database import get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.user import User
from app.schemas.auth import TokenData

router = APIRouter()
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.email == token_data.email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "id": current_user.id}