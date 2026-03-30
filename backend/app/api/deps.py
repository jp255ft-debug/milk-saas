from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app import models
from app.core import security
from app.database import SessionLocal

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
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Prioridade para o Cookie (comum no frontend Next.js)
    token_from_cookie = request.cookies.get("access_token")
    if token_from_cookie:
        token = token_from_cookie.replace("Bearer ", "") if token_from_cookie.startswith("Bearer ") else token_from_cookie
    
    if token is None:
        raise credentials_exception
    
    try:
        payload = security.decode_access_token(token)
        farm_id: str = payload.get("sub")
        if farm_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    farm = db.query(models.Farm).filter(models.Farm.id == farm_id).first()
    if farm is None:
        raise credentials_exception
    return farm

# NOVO: Validador de Plano PRO
def check_pro_plan(current_farm: models.Farm = Depends(get_current_farm)):
    if current_farm.plan_type != "pro":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Funcionalidade disponível apenas no Plano PRO."
        )
    return current_farm