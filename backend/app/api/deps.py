from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app import models
from app.core import security
from app.database import SessionLocal

# === CORREÇÃO: Apontando para a rota de login correta ===
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_farm(
    request: Request,
    db: Session = Depends(get_db),
    token: str | None = Depends(oauth2_scheme),
) -> models.Farm:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Tenta obter token do cookie primeiro
    token_from_cookie = request.cookies.get("access_token")
    if token_from_cookie:
        if token_from_cookie.startswith("Bearer "):
            token = token_from_cookie.replace("Bearer ", "")
        else:
            token = token_from_cookie
    elif token is None:
        raise credentials_exception
    
    try:
        payload = security.decode_access_token(token)
        farm_id: str = payload.get("sub")
        if farm_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception from None  # ← corrigido
    
    farm = db.query(models.Farm).filter(models.Farm.id == farm_id).first()
    if farm is None:
        raise credentials_exception
    
    return farm